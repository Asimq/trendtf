"""
@author: AsimA

Target: Dspace 7.5 backend
Requires: Configration 'config.yml' YML File with the following fields
dspace_server: DSPACE SERVER e.g., http://trendtfrepo21.osl.tib.eu:8080/server
dspace_username: ADMIN USERNAME
dspace_password: ADMIN PASS
For adding more functions review https://wiki.lyrasis.org/display/DSDOC7x/Content+%28Item%29+management

Input Requirment:
1.	CollectionID from DSPACE to which metadata has to be uploaded 
2.	Input JSON DC folder path
3.	Input pdf or txt files folder path (optional) 

This script will login to dspace, and import DC metadata via API and upload a PDF or Text file if required. You can adjust it to upload multiple files.
It will create CSV file with filname, ItemUID, BundleUID, AND FileUID - Based on the ItemUID of each file you can perform operations on it later if needed.
It will also create an error CSV with filename and error message. 
"""

import requests
import yaml
import http.cookies
import json
import os
import time
from datetime import datetime
import csv

dspace_server = ""
dspace_username = ""
dspace_password = ""

xsrf_token = None
set_cookie = None
authorization = None


def load_config(filename):
    try:
        with open(filename, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Could not find {filename}.")
        return {}

    return config

def set_config_vars(config):
    global dspace_server, dspace_username, dspace_password
    dspace_server = config.get('dspace_server', dspace_server)
    dspace_username = config.get('dspace_username', dspace_username)
    dspace_password = config.get('dspace_password', dspace_password)

def check_login_status():
    global xsrf_token, set_cookie
    url = f"{dspace_server}/api/authn/status"
    headers = {}
    try:
        response = requests.request("GET", url, headers=headers)
        response.raise_for_status()  # raise an exception for 4xx or 5xx status codes
        response_body = response.json()

        if response_body['authenticated'] == False:
            xsrf_token = response.headers.get('DSPACE-XSRF-TOKEN')
            set_cookie = response.headers.get('Set-Cookie')
            return True
        else:
            return False
    except requests.exceptions.RequestException as e:
        print(check_login_status.__name__ + " An error occurred:", e)
        return False


def login_to_dspace():
    global xsrf_token, set_cookie, authorization
    url = f"{dspace_server}/api/authn/login?user={dspace_username}&password={dspace_password}"
    headers = {
      'X-XSRF-TOKEN': xsrf_token,
      'Cookie': set_cookie
    }
    payload={}
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # raise an exception for 4xx or 5xx status codes

        xsrf_token = response.headers.get('DSPACE-XSRF-TOKEN')
        set_cookie_header = response.headers.get('Set-Cookie')
        cookies = http.cookies.SimpleCookie()
        cookies.load(set_cookie_header)
        set_cookie = cookies['DSPACE-XSRF-COOKIE'].OutputString()
        authorization = response.headers.get('Authorization')
    except requests.exceptions.RequestException as e:
        print(login_to_dspace.__name__ + " An error occurred:", e)


def verify_login_status():
    url = f"{dspace_server}/api/authn/status"
    try:
        response = requests.request("GET", url, headers={
          'Authorization': authorization,
          'Cookie': set_cookie
        })
        response.raise_for_status()  # raise an exception for 4xx or 5xx status codes
        response_body = response.json()

        return response_body['authenticated']
    except requests.exceptions.RequestException as e:
        print(verify_login_status.__name__ + " An error occurred:", e)
        return False

# create Bundle for item
def createBundle(itemID):
    url = f"{dspace_server}/api/core/items/{itemID}/bundles"  
    
    # Define the headers and payload for the request
    headers = {
        'Content-Type': 'application/json',
        'X-XSRF-TOKEN': xsrf_token,
        'Cookie': set_cookie,
        'Authorization': authorization
    }

    # Bundle must be named ORIGINAL 
    payload = json.dumps({
        "name": "ORIGINAL"
    })
    
    try:
        # create bundle
        response = requests.request("POST", url, headers=headers, data=payload)
        # Extract the item ID from the response
        bundle_uid = response.json()["uuid"]
        return bundle_uid
    except requests.exceptions.RequestException as e:
        print(createBundle.__name__ + " An error occurred:", e)
        return ""

# upload file for an item 
def upload_file(bundle_uid, filepath, filedescription):
    url = f"{dspace_server}/api/core/bundles/{bundle_uid}/bitstreams"  
    
    # Define the headers and payload for the request
    headers = {
        #'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW',
        'X-XSRF-TOKEN': xsrf_token,
        'Cookie': set_cookie,
        'Authorization': authorization
    }
    try:
        # Define the file to be uploaded
        # Open the file
        fileToUpload = open(filepath, "rb")
        
        # Get the file's name and extension
        filename = os.path.basename(filepath)
        file_extension = os.path.splitext(filename)[1]

        # Determine the file's MIME type
        mime_type = "application/pdf" if file_extension == ".pdf" else "text/plain"
        # Create the files dictionary
        files = {
            "file": (filename, fileToUpload, mime_type),
            "name": filename,
            "description": filedescription
        }
        # Upload the file to the item
        response = requests.request("POST", url, headers=headers, files=files)
        return response.json()["uuid"]
    except requests.exceptions.RequestException as e:
        print(upload_file.__name__ + " An error occurred:", e)
        return ""

# import metadata as item  
def import_dublincore_metadata(payload, collection):
    url = f"{dspace_server}/api/core/items?owningCollection={collection}"  
    
    # Define the headers and payload for the request
    headers = {
        'Content-Type': 'application/json',
        'X-XSRF-TOKEN': xsrf_token,
        'Cookie': set_cookie,
        'Authorization': authorization
    }
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        # Extract the item ID from the response
        item_id = response.json()["id"]
        return item_id
    except requests.exceptions.RequestException as e:
        print(import_dublincore_metadata.__name__ + " An error occurred:", e)
        return ""



def main():
    # Using DSpace default dublin core metadata schema
    
    # Dspace Collection UID
    collection = ''  # e.g., 1a56ff90-7b75-4372-9e91-efa0c3aea62b
    inputdir = '' #Path to Input DC JSON Metadata e.g., /mnt/drive/metadata/dc_cs_topics2
    inputFilesDir = '' #Path to PDF or text files to upload e.g., /mnt/drive/Pdfs/MASTER/

    # Load configuration from YAML file
    yaml_config = 'config.yml'
    config = load_config(yaml_config)
    
    error_log = []
    item_data = []

    if config:
        set_config_vars(config)
        
        # Check login status and perform tasks
        if check_login_status():
            login_to_dspace()
            start_time = time.time()
            count = 0
            for filename in os.listdir(inputdir):
                if filename.endswith('.json'):
                    try:
                        if not verify_login_status() or time.time() - start_time > 300:
                            login_to_dspace()
                            start_time = time.time()
                        
                        # Import metadata
                        with open(os.path.join(inputdir, filename), 'r', encoding='utf-8') as f:
                            payload = json.dumps(json.load(f))
                            f.close()
                        count += 1
                        print(f"Importing file: {filename} - ProcessedFiles: {count}")
                        
                        itemUID = import_dublincore_metadata(payload, collection)
                    
                        # Create bundle
                        itemBundleUID = createBundle(itemUID)
                    
                        
                        # Upload file
                        txt_filename = os.path.splitext(filename)[0] + '.pdf'
                        txt_filepath = os.path.join(inputFilesDir, txt_filename)
                        itemFileUID = upload_file(itemBundleUID, txt_filepath, "Report")
                        
                        # Save itemUID, itemBundleUID, and itemFileID
                        item_data.append((filename, itemUID, itemBundleUID, itemFileUID))
                    except Exception as e:
                        error_log.append((filename, str(e)))
        else:
            print("Couldn't connect to Dspace")

    # Save error log
    error_log_filename = 'error_log_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(error_log_filename, 'w') as f:
        for error_entry in error_log:
            f.write("{}: {}\n".format(*error_entry))

    # Save item data as CSV
    csv_filename = 'item_data_{}.csv'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename','ItemUID', 'ItemBundleUID', 'ItemFileID'])
        for data_entry in item_data:
            writer.writerow(data_entry)


if __name__ == '__main__':
    main()
