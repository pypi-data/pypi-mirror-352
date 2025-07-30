
# built-in modules
import re
import os
import warnings
import logging
from functools import reduce

# 3rd party modules
import numpy as np
import pandas as pd

# project modules
from .._core.commons import get_all_sites
from .._core import corrections

logger = logging.getLogger('wvlt.eddypro_tools')

def read_eddypro_metadata_file(filename):
    metadata = {}
    with open(filename, 'r') as file:
        section = None
        for line in file:
            line = line.strip()
            if line.startswith(';') or not line:
                continue  # Skip comments and empty lines
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]  # Extract section name
                metadata[section] = {}
            else:
                key, value = line.split('=', 1)
                metadata[section][key.strip()] = value.strip()
    return metadata


def get_eddypro_output(site_name=None, treated=True, **kwargs):
    if site_name is None:
        return get_all_sites(get_eddypro_output, **kwargs)
    mergeorconcat = kwargs.get('mergeorconcat', 'merge')
    folder        = kwargs.get('folder', 'data')
    
    ep_read_params = {'skiprows': [0,2], 'na_values': [-9999, 'NAN']}
    
    ep_path = os.path.join(folder, site_name, 'eddypro_output')

    files = {'FLUX': [], 'FLXNT': [], 'QCQA': [], 'META': []}
    for name in os.listdir(ep_path):
        if name.endswith('.csv'):
            if re.findall('_full_output_', name):
                if name.endswith('_adv.csv'):
                    files['FLUX'] += [pd.read_csv(os.path.join(ep_path, name), **ep_read_params)]
                else:
                    files['FLUX'] += [pd.read_csv(os.path.join(ep_path, name), na_values=[-9999, 'NAN'])]
            elif re.findall('_fluxnet_', name):
                flxnt_last = pd.read_csv(os.path.join(ep_path, name), na_values=[-9999, 'NAN'])
                flxnt_last["date"] = pd.to_datetime(flxnt_last["TIMESTAMP_START"], format='%Y%m%d%H%M').dt.strftime('%Y-%m-%d')
                flxnt_last["time"] = pd.to_datetime(flxnt_last["TIMESTAMP_START"], format='%Y%m%d%H%M').dt.strftime('%H:%M')
                files['FLXNT'] += [flxnt_last]
                del flxnt_last
            elif re.findall('_qc_details_', name):
                if name.endswith('_adv.csv'):
                    files['QCQA'] += [pd.read_csv(os.path.join(ep_path, name), **ep_read_params)]
                else:
                    files['QCQA'] += [pd.read_csv(os.path.join(ep_path, name), na_values=[-9999, 'NAN'])]
            elif re.findall('_metadata_', name):
                files['META'] += [pd.read_csv(os.path.join(ep_path, name), na_values=[-9999, 'NAN'])]
    
    for k in [k for k in list(files.keys()) if not files[k]]:
        del([files[k]])

    for k in files.keys():
        if len(files[k]) == 1:
            files[k] = files[k][0]
        elif mergeorconcat == 'concat':
            files[k] = pd.concat(files[k])
        else:
            files[k] = reduce(lambda left, right: pd.merge(
                left, right, on=["date", 'time'], how="outer", suffixes=('', '_DUP')), files[k])
    
    data = pd.DataFrame(files.pop('FLUX', {}))
    for name, dat in files.items():
        data = pd.merge(data, dat, on=["date", 'time'], how="outer", suffixes=('', f'_{name}'))
    
    data['TIMESTAMP'] = pd.to_datetime(data.date + ' ' + data.time)#.dt.tz_localize('UTC')
    
    if treated:
        # Convert to UTC
        data['TIMESTAMP_UTC'] = data['TIMESTAMP'].dt.tz_localize('UTC')

        # Despike because open path analysers can be noisy
        data['air_molar_volume_despiked'] = corrections.mauder2013(data.air_molar_volume, 5)
        data['Vd'] = (data.air_molar_volume_despiked * data.air_pressure /
                            (data.air_pressure - data.e))
        # Make wet from dry
        data['Va'] = (data.air_molar_volume_despiked * data.air_pressure /
                            (data.air_pressure - data.e))
    return data


def get_eddypro_cospectra(site_name=None, x='natural_frequency', y='f_nat*cospec(w_co2)/cov(w_co2)', folder='data', subfolder='', help=False):
    assert (x is not None and y is not None) or (help)
    if site_name is None:
        return get_all_sites(get_eddypro_cospectra, x=x, y=y, folder=folder, subfolder=subfolder, help=help)
    
    ep_path = os.path.join(folder, site_name, 'output/eddypro_output', subfolder, 'eddypro_binned_cospectra')
    
    if not os.path.exists(ep_path): return None
    files = []
    for name in os.listdir(ep_path):
        if name.endswith('.csv'):
            if re.findall('_binned_cospectra_', name):
                binned_cosp = pd.read_csv(os.path.join(ep_path, name), skiprows=11, na_values=[-9999, 'NAN'])
                if help: 
                    print(binned_cosp.columns)
                    return
                if x not in binned_cosp.columns or y not in binned_cosp.columns: continue
                binned_cosp.dropna(subset=[x], inplace=True)
                binned_cosp = binned_cosp[[x, y]]
                binned_cosp['TIMESTAMP'] = name.split('_')[0]
                binned_cosp = binned_cosp.pivot(index='TIMESTAMP', columns=x, values=y).reset_index(drop=False)
                binned_cosp.columns = [c for c in binned_cosp.columns]
                files += [binned_cosp]
    
    if len(files) == 1:
        data = files[0]
    else:
        data = pd.concat(files)
    
    data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], format='%Y%m%d-%H%M')
    return data


def extract_info_from_eddypro_setup(eddypro=None, metadata=None):
    """
    Extracts information from EddyPro setup and metadata files and returns a dictionary.

    Parameters:
    - eddypro: Path to the EddyPro setup file.
    - metadata: Path to the metadata file.

    Returns:
    - A dictionary containing extracted information.
    """    
    args = {}

    if eddypro:
        eddypro_setup = read_eddypro_metadata_file(eddypro)

        metadata = metadata or eddypro_setup['Project']['proj_file'] or str(eddypro).rsplit('.', 1)[
            0] + '.metadata'

        args['site_name'] = eddypro_setup['Project']['project_id']
        args['input_path'] = eddypro_setup['Project']['out_path'] + \
            '/eddypro_raw_datasets/level_6'
        args['output_folderpath'] = eddypro_setup['Project']['out_path'] + \
            '/wavelet_flux'
        args['datetimerange'] = (
            eddypro_setup['Project']['pr_start_date'].replace('-', '') +
            eddypro_setup['Project']['pr_start_time'].replace(':', '') + '-' +
            eddypro_setup['Project']['pr_end_date'].replace('-', '') +
            eddypro_setup['Project']['pr_end_time'].replace(':', '')
        )
        args['fileduration'] = int(
            eddypro_setup['RawProcess_Settings']['avrg_len'])

        try:
            gas4_col = eddypro_setup['Project']['col_n2o']
            eddypro_metad = read_eddypro_metadata_file(metadata)
            if (not gas4_col) or (str(gas4_col) != '0'):
                args['gas4_name'] = eddypro_metad['FileDescription'][f'col_{gas4_col}_variable']
        except Exception as e:
            print(f"Error extracting gas4 name: {e}")

    if metadata:
        eddypro_metad = read_eddypro_metadata_file(metadata)
        args['acquisition_frequency'] = int(
            float(eddypro_metad['Timing']['acquisition_frequency']))

    if eddypro:
        args['variables_available'] = ['u', 'v', 'w'] + [k for k in ['co2',
                                                                     'h2o', 'ch4'] if float(eddypro_setup['Project'][f'col_{k}']) > 0]

    if metadata and float(eddypro_setup['Project']['col_n2o']) > 0:
        gas4 = eddypro_metad['FileDescription'][f"col_{eddypro_setup['Project']['col_n2o']}_variable"]
        if gas4:
            args['variables_available'] = args.get(
                'variables_available', []) + [gas4]

    return args


def update_args_with_extracted_info(args, extracted_info):
    """
    Updates the args dictionary with the extracted information.

    Parameters:
    - args: The dictionary to be updated.
    - extracted_info: The dictionary containing extracted information.

    Returns:
    - The updated args dictionary.
    """
    for key, value in extracted_info.items():
        if key not in args or args[key] is None:
            args[key] = value
    return args
