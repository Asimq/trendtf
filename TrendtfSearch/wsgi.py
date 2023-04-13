from flask import Flask,request
from werkzeug.middleware.proxy_fix import ProxyFix
from controller import init_controller
import yaml


def load_config(file_path='config.yml'):
    with open(file_path, 'r') as config_file:
        return yaml.safe_load(config_file)

config = load_config()


app = Flask(__name__, template_folder=config['flask']['template_folder'])
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['APPLICATION_ROOT'] = f"/{config['flask']['application_root']}"
# Set the preferred URL scheme to HTTPS
app.config['PREFERRED_URL_SCHEME'] = 'https'


# Use the ProxyFix middleware to handle reverse proxy headers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.before_request
def set_server_name():
    request.environ['SCRIPT_NAME'] = app.config.get('APPLICATION_ROOT', '')
    # Set the base URL depending on the request scheme
    if request.environ.get('wsgi.url_scheme') == 'https':
        app.config['BASE_URL'] = f"https://{config['flask']['https_host']}/{config['flask']['application_root']}"
    else:
        app.config['BASE_URL'] = f"http://{config['flask']['host']}:{config['flask']['port']}"
    
""" 
    # Print the request information
    print('Request: {} {}'.format(request.method, request.url))
    print('Headers: {}'.format(request.headers))
    print('Script Name: {}'.format(request.environ.get('SCRIPT_NAME')))
    print('URL Scheme: {}'.format(request.environ.get('wsgi.url_scheme')))
"""

search_controller = init_controller(app, config)


if __name__ == '__main__':
    flask_config = config['flask']
    app.run(host=flask_config['host'], port=flask_config['port'], debug=flask_config['debug'])
