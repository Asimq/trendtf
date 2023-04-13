import requests
import os
import json


class DspaceItem:

    def __init__(self, client):
        self.client = client

    def create_bundle(self, item_id):
        url = f"{self.client.server}/api/core/items/{item_id}/bundles"
        headers = {
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': self.client.xsrf_token,
            'Cookie': self.client.set_cookie,
            'Authorization': self.client.authorization
        }
        payload = json.dumps({
            "name": "ORIGINAL"
        })

        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            bundle_uid = response.json()["uuid"]
            return bundle_uid
        except requests.exceptions.RequestException as e:
            print("create_bundle: An error occurred:", e)
            return ""

    def upload_file(self, bundle_uid, filepath, filedescription):
        url = f"{self.client.server}/api/core/bundles/{bundle_uid}/bitstreams"
        headers = {
            'X-XSRF-TOKEN': self.client.xsrf_token,
            'Cookie': self.client.set_cookie,
            'Authorization': self.client.authorization
        }

        try:
            file_to_upload = open(filepath, "rb")
            filename = os.path.basename(filepath)
            file_extension = os.path.splitext(filename)[1]
            mime_type = "application/pdf" if file_extension == ".pdf" else "text/plain"

            files = {
                "file": (filename, file_to_upload, mime_type),
                "name": filename,
                "description": filedescription
            }

            response = requests.request("POST", url, headers=headers, files=files)
            return response.json()["uuid"]
        except requests.exceptions.RequestException as e:
            print("upload_file: An error occurred:", e)
            return ""
