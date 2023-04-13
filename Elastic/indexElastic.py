"""
@author: AsimA

Target: Elasticsearch Index

Input Requirment:
1.	Path of data in JSON
2.	Name of Elastic Index
3.	URL of Elastic main node

This script will index the JSON data into the given Elastic index 
"""

import os
import json
import requests


def index_documents(json_files, index_name, es_url):
    """
    Index documents into Elasticsearch index.
    """
    error_files = []
    for json_file in json_files:
        with open(json_file, 'r') as f:
            try:
                json_data = json.load(f)
                print(f"loaded {json_file}")
            except json.JSONDecodeError:
                error_files.append(json_file)
                print(f"Error loading {json_file}")
                continue
            url = f"{es_url}/{index_name}/_doc"
            response = requests.post(url, data=json.dumps(json_data), headers={"Content-Type": "application/json"})
            if response.status_code != 201:
                error_files.append(json_file)
                print(f"Couldn't index {json_file} \n {response.content}")
                continue
            print(f"Successfully indexed document in file {json_file}")
    if error_files:
        with open('error_files.txt', 'w') as f:
            f.write('\n'.join(error_files))

def main():
    """
    Main function that reads all JSON files from input folder and indexes them into Elasticsearch index.
    """
    # Path of data in JSON
    input_folder = ''
    # Elastic Index Name
    index_name = ''
    #Elastic Main Node e.g., http://trendtf22.osl.tib.eu:9200
    es_url = ''

    json_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.json')]
    index_documents(json_files, index_name, es_url)

if __name__ == '__main__':
    main()
