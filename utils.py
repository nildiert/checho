import os
import shutil
import requests
from tqdm import tqdm

def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

def download_image(url, path, error_log_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        tqdm.write(f"Downloading image from {url[:50]}...")  # Print a part of the URL being downloaded
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        with open(path, "wb") as file:
            file.write(response.content)
        return True
    except requests.RequestException as e:
        error_message = f"Failed to download image from {url}. Reason: {e}\n\n"
        with open(error_log_path, "a") as log_file:
            log_file.write(error_message)
        tqdm.write(error_message.strip())
        return False
