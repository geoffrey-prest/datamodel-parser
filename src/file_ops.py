# file_ops.py

import json
import logging
import os

def get_file_content(file_path: str, encoding: str):
    """
    Reads the content of a file and returns it as a list of lines.
    Args:
        file_path (str): The path to the file to be read.
        encoding (str): The character encoding used in the file (e.g., 'utf-8').
    Returns:
        list: A list of lines read from the file.
    """

    file_content = []

    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:
            file_content = file.readlines()
    except FileNotFoundError: 
        logging.error(f"The file at {file_path} was not found.", exc_info=True)
    except OSError as e:
        logging.error(f"Error opening file {file_path}: {e}", exc_info=True)

    return file_content

def is_valid_directory(directory: str):
    """
    Validates the given directory path.
    Args:
        directory (str): The directory path to be validated.
    Returns:
        bool: True if the directory is valid, False otherwise.
    """
    is_valid = True

    if not os.path.isdir(directory):
        logging.error(f"Error: The given directory '{directory}' does not exist or is not a directory.", exc_info=True)
        is_valid = False
    elif not os.access(directory, os.R_OK):
        logging.error(f"Error: The given directory '{directory}' is not readable.", exc_info=True)
        is_valid = False

    return is_valid

def write_json_to_file(data_model: dict, file_path: str, encoding: str):
    """
    Stores the given data model in a JSON file.
    Args:
        data_model (dict): The data model to be stored in the JSON file.
        directory (str): The directory where the JSON file will be saved.
        encoding (str): The encoding to be used for the JSON file.
    Returns:
        str: The path to the output file.
    """
    
    try:
        with open(file_path, 'w', encoding=encoding, errors='replace') as outfile:
            json.dump(data_model, outfile, indent=4)
    except FileNotFoundError: 
        logging.error(f"The file at {file_path} was not found.", exc_info=True)
    except OSError as e:
        logging.error(f"Error opening file {file_path}: {e}", exc_info=True)

    return file_path

def write_text_to_file(file_path: str, encoding: str, content:str):
    try:
        with open(file_path, 'w') as file:
            file.write(content)
    except FileNotFoundError: 
        logging.error(f"The file at {file_path} was not found.", exc_info=True)
    except OSError as e:
        logging.error(f"Error opening file {file_path}: {e}", exc_info=True)