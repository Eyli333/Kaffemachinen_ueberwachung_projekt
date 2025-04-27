import os
import json
import base64
import requests

def send_data_to_api(folder_path, api_url):
    """
    Retrieves data from meta.json and mel_spectrogram1.png in a folder
    and sends it to the specified Flask API, using 'cycle_id' as the machine ID.

    Args:
        folder_path (str): The path to the folder containing the files.
        api_url (str): The URL of the Flask API endpoint to receive the data.
    """

    meta_file_path = os.path.join(folder_path, "meta.json")
    image_file_path = os.path.join(folder_path, "mel_spectrogram.png")

    if not os.path.exists(meta_file_path):
        print(f"Error: The meta.json file cannot be found in '{folder_path}'.")
        print(meta_file_path)
        return

    if not os.path.exists(image_file_path):
        print(f"Warning: The file mel_spectrogram1.png cannot be found in '{folder_path}'. The image will not be sent.")
        image_base64 = None
    else:
        try:
            with open(image_file_path, "rb") as image_file:
                image_content = image_file.read()
                image_base64 = base64.b64encode(image_content).decode('utf-8')
            print(f"Image '{image_file_path}' base64 encoded.")
        except Exception as e:
            print(f"Error when reading image '{image_file_path}': {e}")
            image_base64 = None

    try:
        with open(meta_file_path, "r") as f:
            metadata = json.load(f)
            print(f"meta.json data read.")
    except Exception as e:
        print(f"Error reading meta.json file: {e}")
        return

    # Extract cycle_id as the machine ID
    machine_id = str(metadata.get("machine_id"))
    if not machine_id:
        print("Error: 'cycle_id' not found in meta.json. Cannot determine machine ID.")
        return

    # Create the API payload
    payload = {
        "machine_id": machine_id,
        "meta": metadata,
        "image_base64": image_base64,
        "filename": "mel_spectrogram1.png"
    }

    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # exception with http error status codes
        print(f"Data successfully sent to the API for machine ID '{machine_id}'. Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request to API: {e}")
    except json.JSONDecodeError:
        print(f"Error decoding the API JSON response.")

if __name__ == "__main__":

    target_folder = "D:\Documents\M1\Musteranalyse & MI\Kaffe_projekt\CNN\dataToSend"  # Folder to be processed
    # target_folder = "testFolderData/"  # Folder to be processed
    if not os.path.exists(target_folder):
        print(f"Error: The folder '{target_folder}' doesn't exist.")
        exit(1)
    # api_endpoint_url = "http://192.168.0.139:8080"  # New API endpoint URL
    api_endpoint_url = "http://127.0.0.1:8080/upload_machine_data"  # New API endpoint URL
    # api_endpoint_url = "https://eyli.pythonanywhere.com/upload_machine_data"  # New API endpoint URL

    send_data_to_api(target_folder, api_endpoint_url)
