import requests
import http.cookies


class DspaceClient:

    def __init__(self, server, username, password):
        self.server = server
        self.username = username
        self.password = password
        self.xsrf_token = None
        self.set_cookie = None
        self.authorization = None

    def check_login_status(self):
        url = f"{self.server}/api/authn/status"
        headers = {}
        try:
            response = requests.request("GET", url, headers=headers)
            response.raise_for_status()
            response_body = response.json()

            if response_body['authenticated'] == False:
                self.xsrf_token = response.headers.get('DSPACE-XSRF-TOKEN')
                self.set_cookie = response.headers.get('Set-Cookie')
                return True
            else:
                return False
        except requests.exceptions.RequestException as e:
            print("check_login_status: An error occurred:", e)
            return False

    def login(self):
        url = f"{self.server}/api/authn/login?user={self.username}&password={self.password}"
        headers = {
            'X-XSRF-TOKEN': self.xsrf_token,
            'Cookie': self.set_cookie
        }
        payload = {}
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            response.raise_for_status()

            self.xsrf_token = response.headers.get('DSPACE-XSRF-TOKEN')
            set_cookie_header = response.headers.get('Set-Cookie')
            cookies = http.cookies.SimpleCookie()
            cookies.load(set_cookie_header)
            self.set_cookie = cookies['DSPACE-XSRF-COOKIE'].OutputString()
            self.authorization = response.headers.get('Authorization')
        except requests.exceptions.RequestException as e:
            print("login: An error occurred:", e)

    def verify_login_status(self):
        url = f"{self.server}/api/authn/status"
        try:
            response = requests.request("GET", url, headers={
                'Authorization': self.authorization,
                'Cookie': self.set_cookie
            })
            response.raise_for_status()
            response_body = response.json()

            return response_body['authenticated']
        except requests.exceptions.RequestException as e:
            print("verify_login_status: An error occurred:", e)
            return False
