# csv_service.py

import csv
import os

def save_to_csv(file_path, data_dict, headers=None):
    """Saves a dictionary of data to a CSV file, adding headers if the file is new.

    Parameters:
        file_path (str): Path to the CSV file where data will be saved.
        data_dict (dict): Data to be written as a dictionary.
        headers (list, optional): List of headers for the CSV file. If not provided, use data_dict keys.
    """
    file_exists = os.path.isfile(file_path)
    mode = 'a' if file_exists else 'w'
    with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
        if headers is None:
            headers = data_dict.keys()
        writer = csv.DictWriter(csvfile, fieldnames=headers)

        if not file_exists:
            writer.writeheader()  # Write headers only if the file is being created

        writer.writerow(data_dict)

def read_from_csv(file_path):
    """Reads rows from a CSV file and returns them as a list of dictionaries.

    Parameters:
        file_path (str): Path to the CSV file to read from.

    Returns:
        List[Dict]: A list of rows from the CSV file, each row represented as a dictionary.
    """
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return [row for row in reader]
