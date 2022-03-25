import requests

from config import config

URL = config['prtg']['import_api_url']
TOKEN = config['prtg']['import_api_token']
TEMPLATE_GROUP = config['prtg']['import_api_token']
TEMPLATE_DEVICE = config['prtg']['import_api_token']

def init_prtg(company_name: str,
             site_name: str,
             probe_id: int,
             unpause: bool,
             prtg_url: str,
             username: str,
             password: str,
             is_passhash: bool):
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
        'companyName': company_name,
        'siteName': site_name,
        'probeId': probe_id,
        'unpause': unpause,
        'prtgUrl': prtg_url,
        'username': username,
        'password': password,
        'isPasshash': is_passhash,
        'templateGroup': TEMPLATE_GROUP,
        'templateDevice': TEMPLATE_DEVICE
    }

    response = requests.post(url, params=params)
    response.raise_for_status()
    return response.text
