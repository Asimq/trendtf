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

import os
import json
import time
from datetime import datetime
import csv

from config_loader import ConfigLoader
from dspace_client import DspaceClient
from metadata_importer import MetadataImporter
from dspace_item import DspaceItem

def main():
    # Using DSpace default dublin core metadata schema

    # Dspace Collection UID
    collection = ''  # e.g., 1a56ff90-7b75-4372-9e91-efa0c3aea62b
    inputdir = ''  # Path to Input DC JSON Metadata e.g., /mnt/drive/metadata/dc_cs_topics2
    input_files_dir = ''  # Path to PDF or text files to upload e.g., /mnt/drive/Pdfs/MASTER/

    # Load configuration from YAML file
    yaml_config = 'config.yml'
    config_loader = ConfigLoader(yaml_config)
    config = config_loader.load_config()

    error_log = []
    item_data = []

    if config:
        dspace_client = DspaceClient(config)
        dspace_client.login()

        if dspace_client.check_login_status():
            start_time = time.time()
            metadata_importer = MetadataImporter(dspace_client)
            dspace_item = DspaceItem(dspace_client)
            count = 0

            for filename in os.listdir(inputdir):
                if filename.endswith('.json'):
                    try:
                        if not dspace_client.verify_login_status() or time.time() - start_time > 300:
                            dspace_client.login()
                            start_time = time.time()

                        with open(os.path.join(inputdir, filename), 'r', encoding='utf-8') as f:
                            payload = json.dumps(json.load(f))
                            f.close()

                        count += 1
                        print(f"Importing file: {filename} - ProcessedFiles: {count}")

                        item_uid = metadata_importer.import_dublincore_metadata(payload, collection)
                        item_bundle_uid = dspace_item.create_bundle(item_uid)

                        txt_filename = os.path.splitext(filename)[0] + '.pdf'
                        txt_filepath = os.path.join(input_files_dir, txt_filename)
                        item_file_uid = dspace_item.upload_file(item_bundle_uid, txt_filepath, "Report")

                        item_data.append((filename, item_uid, item_bundle_uid, item_file_uid))

                    except Exception as e:
                        error_log.append((filename, str(e)))

        else:
            print("Couldn't connect to Dspace")

    error_log_filename = 'error_log_{}.txt'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(error_log_filename, 'w') as f:
        for error_entry in error_log:
            f.write("{}: {}\n".format(*error_entry))

    csv_filename = 'item_data_{}.csv'.format(datetime.now().strftime('%Y%m%d_%H%M%S'))
    with open(csv_filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'ItemUID', 'ItemBundleUID', 'ItemFileID'])
        for data_entry in item_data:
            writer.writerow(data_entry)


if __name__ == '__main__':
    main()
