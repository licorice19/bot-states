import json
import logging
import os

logger = logging.getLogger(__name__)

def key_str_to_int(input_dict: dict) -> dict:
    """
    Convert string keys in a dictionary to integers.
    
    Args:
        input_dict (dict): A dictionary with string keys.
        
    Returns:
        dict: A new dictionary with integer keys.
    """
    return {int(k): v for k, v in input_dict.items() if k.isdigit()}

def load_json(file_path: str = 'data.json') -> dict:
    """
    Load dictionary from a JSON file into a dictionary.
    
    Args:
        file_path (str): The path to the JSON file.
        
    Returns:
        dict: A dictionary with some keys and values loaded from the JSON file.
    """
    logger.info(f"Attempting to load barcodes from {file_path}.")
    loading_dict = None
    if os.path.exists(file_path):
        logger.info(f"Loading barcodes from {file_path}.")
        with open(file_path, 'r') as file:
            loading_dict = json.load(file)
    
    if loading_dict is None:
        logger.warning(f"No data found in {file_path}. Returning an empty dictionary.")
        loading_dict = {}

    loading_dict = key_str_to_int(loading_dict)

    return loading_dict

def save_json(saving_dict: dict, file_path: str = 'data.json') -> None:
    """
    Save a dictionary of barcodes to a JSON file.
    
    Args:
        file_path (str): The path to the JSON file be saved.
        saving_dict (dict): A dictionary with some keys and values to save to the JSON file.
    """
    logger.info(f"Saving barcodes to {file_path}.")
    with open(file_path, 'w') as file:
        json.dump(saving_dict, file, indent=4)