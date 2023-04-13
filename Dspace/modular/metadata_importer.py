import requests


class MetadataImporter:

    def __init__(self, client):
        self.client = client

    def import_dublincore_metadata(self, payload, collection):
        url = f"{self.client.server}/api/core/items?owningCollection={collection}"
        headers = {
            'Content-Type': 'application/json',
            'X-XSRF-TOKEN': self.client.xsrf_token,
            'Cookie': self.client.set_cookie,
            'Authorization': self.client.authorization
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            item_id = response.json()["id"]
            return item_id
        except requests.exceptions.RequestException as e:
            print("import_dublincore_metadata: An error occurred:", e)
            return ""
