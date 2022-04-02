import requests

from config import config

URL = config['prtg']['import_api_url']
TOKEN = config['prtg']['import_api_token']
PROBE_ID = config['prtg'].getint('probe_id')
TEMPLATE_GROUP = config['prtg'].getint('template_group')
TEMPLATE_DEVICE = config['prtg'].getint('template_device')
USERNAME = config['prtg']['username']
PASSWORD = config['prtg']['password']
IS_PASSHASH = config['prtg'].getboolean('is_passhash')
UNPAUSE = config['prtg'].getboolean('unpause')
COMPANY = config['prtg']['company']
SITE_NAME = config['prtg']['site_name']

def init_prtg(prtg_url: str,
             username: str = USERNAME,
             password: str = PASSWORD):
    '''Call external XSAutomate API to stand up PRTG from SNow.

    Args:
        company_name (str): Name of the test drive
        site_name (str): Name of test drive site

    Returns:
        str: Text response of XSAutomate API
    '''

    url = URL
    params = {
        'token': TOKEN,
        'companyName': COMPANY,
        'siteName': SITE_NAME,
        'probeId': PROBE_ID,
        'unpause': UNPAUSE,
        'prtgUrl': prtg_url,
        'username': username,
        'password': password,
        'isPasshash': IS_PASSHASH,
        'templateGroup': TEMPLATE_GROUP,
        'templateDevice': TEMPLATE_DEVICE
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.text
