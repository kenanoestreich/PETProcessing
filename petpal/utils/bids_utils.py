"""
This module contains utilities for handling `Brain Imaging Data Structure (BIDS) <https://bids.neuroimaging.io/>`_ datasets. It simplifies the
creation and management of BIDS projects, offering functions for building project scaffolds, handling file paths,
and managing neuroimaging data files. Key features include scaffolding BIDS projects, caching file paths for efficient
retrieval, and supporting various neuroimaging file types through integration with `nibabel`.
"""
import json
import os
import shutil
import warnings
import numpy
import pathlib
from bids_validator import BIDSValidator
from nibabel.filebasedimages import FileBasedImage
from nibabel.nifti1 import Nifti1Image

def create_json(**kwargs) -> dict:
    """
    Creates a dictionary from provided keyword arguments.

    Args:
        **kwargs: Arbitrary keyword arguments.

    Returns:
        A dictionary constructed from the keyword arguments.
    """
    return kwargs


def update_json(json_dict: dict,
                **kwargs) -> dict:
    """
    Updates an existing JSON dictionary with additional key-value pairs.

    Args:
        json_dict (dict): The original dictionary to be updated.
        **kwargs: Arbitrary keyword arguments to update json_dict with.

    Returns:
        The updated dictionary.
    """
    json_dict.update(**kwargs)
    return json_dict


def save_json(json_dict: dict,
              filepath: str) -> None:
    """
    Saves a dictionary as a JSON file at the specified filepath.

    Args:
        json_dict (dict): The dictionary to save as JSON.
        filepath (str): The destination file path. If the path does not end with ".json", it will be appended.

    Note:
        The JSON file is formatted with an indentation of 4 spaces for readability.
    """
    if not filepath.endswith(".json"):
        filepath += ".json"
    with open(filepath, 'w') as file:
        json.dump(json_dict, file, indent=4)
        file.write('\n')


def save_array_as_tsv(array: numpy.array,
                      filepath: str) -> None:
    """
    Saves a NumPy array as a TSV (Tab-Separated Values) file.

    Args:
        array (numpy.array): The NumPy array to save.
        filepath (str): The destination file path for the TSV file.

    Note:
        Each row of the array is saved as a separate line in the TSV file.
    """
    numpy.savetxt(filepath, array, delimiter='\t', fmt='%s')


def save_tsv_simple(filepath: str, data: list) -> None:
    """
    Saves a list of lists as a TSV (Tab-Separated Values) file.

    Args:
        filepath (str): The destination file path for the TSV file.
        data (list): A list of lists, where each sublist represents a row in the TSV file.
    """
    with open(filepath, 'w', encoding='utf-8') as file:
        for row in data:
            line = '\t'.join(row)
            file.write(line + '\n')


def load_tsv_simple(filepath: str) -> list:
    """
    Loads a TSV (Tab-Separated Values) file from the specified filepath and returns its content as a list of lists.

    Args:
        filepath (str): The path to the TSV file to be loaded.

    Returns:
        A list of lists, where each sublist represents a row in the TSV file, split by tabs.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        data = [line.strip().split('\t') for line in file]
    return data


def validate_filepath_as_bids(filepath: str) -> bool:
    """
    Validate whether a given filepath conforms to the Brain Imaging Data Structure (BIDS) standard.

    Args:
        filepath (str): The path to the file to be validated.

    Returns:
        bool: True if the file conforms to the BIDS standard, False otherwise.

    """
    validator = BIDSValidator()
    return validator.is_bids(filepath)


def validate_directory_as_bids(project_path: str) -> bool:
    """
    Validate whether all files in a given directory and its subdirectories (excluding specified ones)
    conform to the Brain Imaging Data Structure (BIDS) standard.

    Args:
        project_path (str): The root directory of the project to validate.

    Returns:
        bool: True if all files in the directory conform to the BIDS standard, False if any do not.

    Raises:
        FileNotFoundError: If the provided project_path does not exist or is inaccessible.

    Notes:
        Excludes directories typically not needed for BIDS validation, such as 'code', 'derivatives',
        'sourcedata', '.git', and 'stimuli'. Also skips directories starting with 'sub-' to focus on top-level structure.
    """
    excluded_dirs = {'code', 'derivatives', 'sourcedata', '.git', 'stimuli'}
    all_passed = True
    failed_file_paths = []

    for root, dirs, files in os.walk(project_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('sub-')]
        for file in files:
            filepath = os.path.join(root, file)
            if not validate_filepath_as_bids(filepath):
                failed_file_paths.append(filepath)
                all_passed = False

    if failed_file_paths:
        print("Failed file paths:")
        for path in failed_file_paths:
            print(path)
    else:
        print("All files passed validation.")

    return all_passed


def parse_path_to_get_subject_and_session_id(path):
    """
    Parses a file path to extract subject and session IDs formatted according to BIDS standards.

    This function expects the file name in the path to contain segments starting with 'sub-' and 'ses-'.
    If these are not found, it returns default values indicating unknown IDs.

    Args:
        path (str): The file path to extract identifiers from.

    Returns:
        tuple: A tuple containing the subject ID and session ID.
    """
    filename = pathlib.Path(path).name
    if ('sub-' in filename) and ('ses-' in filename):
        sub_ses_ids = filename.split("_")[:2]
        sub_id = sub_ses_ids[0].split('sub-')[-1]
        ses_id = sub_ses_ids[1].split('ses-')[-1]
        return sub_id, ses_id
    else:
        return "XXXX", "XX"

def snake_to_camel_case(snake_str):
    """
    Converts a snake_case string to CamelCase.

    The function breaks the input string by underscores and capitalizes each segment to generate CamelCase.

    Args:
        snake_str (str): The snake_case string to convert.

    Returns:
        str: The converted CamelCase string.
    """
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))

def gen_bids_like_filename(sub_id: str, ses_id: str, suffix: str= 'pet', ext: str= '.nii.gz', **extra_desc) -> str:
    """
    Generates a filename following BIDS convention including subject and session information.

    The function constructs filenames by appending additional descriptors and file suffix with extension.

    Args:
        sub_id (str): The subject identifier.
        ses_id (str): The session identifier.
        suffix (str, optional): The suffix indicating the data type. Defaults to 'pet'.
        ext (str, optional): The file extension. Defaults to '.nii.gz'.
        **extra_desc: Additional keyword arguments for any extra descriptors.

    Returns:
        str: A BIDS-like formatted filename.
    """
    sub_ses_pre = f'sub-{sub_id}_ses-{ses_id}'
    file_parts = [sub_ses_pre, ]
    for name, val in extra_desc.items():
        file_parts.append(f'{name}-{val}')
    file_parts.append(f'{suffix}{ext}')
    file_name = "_".join(file_parts)
    return file_name

def gen_bids_like_dir_path(sub_id: str, ses_id: str, modality: str='pet', sup_dir: str= '../') -> str:
    """
    Constructs a directory path following BIDS structure with subject and session subdirectories.

    Args:
        sub_id (str): The subject identifier.
        ses_id (str): The session identifier.
        modality (str, optional): Modality directory name. Defaults to 'pet'.
        sup_dir (str, optional): The parent directory path. Defaults to '../'.

    Returns:
        str: A BIDS-like directory path.
    """
    path_parts = [f'{sup_dir}', f'sub-{sub_id}', f'ses-{ses_id}', f'{modality}']
    return os.path.join(*path_parts)

def gen_bids_like_filepath(sub_id: str, ses_id: str, bids_dir:str ='../',
                           modality: str='pet', suffix:str='pet', ext='.nii.gz', **extra_desc) -> str:
    """
    Creates a full file path using BIDS-like conventions for both directory structure and filename.

    It combines directory and file generation to provide an organized output path.

    Args:
        sub_id (str): The subject identifier.
        ses_id (str): The session identifier.
        bids_dir (str, optional): Base directory for BIDS data. Defaults to '../'.
        modality (str, optional): The type of modality. Defaults to 'pet'.
        suffix (str, optional): Suffix indicating the type. Defaults to 'pet'.
        ext (str, optional): The file extension. Defaults to '.nii.gz'.
        **extra_desc: Additional keyword arguments for any extra descriptors.

    Returns:
        str: Full file path in BIDS-like structure.
        
    See Also:
        - :func:`gen_bids_like_filename`
        - :func:`gen_bids_like_dir_path`
        
    """
    filename = gen_bids_like_filename(sub_id=sub_id, ses_id=ses_id, suffix=suffix, ext=ext, **extra_desc)
    filedir  = gen_bids_like_dir_path(sub_id=sub_id, ses_id=ses_id, sup_dir=bids_dir, modality=modality)
    return os.path.join(filedir, filename)
