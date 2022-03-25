import pysnow

from config import config

SNOW_INSTANCE = config['snow']['snow_instance']
SNOW_USER = config['snow']['api_user']
SNOW_PASS = config['snow']['api_password']

# ServiceNow Client
SNOW_CLIENT = pysnow.Client(instance=SNOW_INSTANCE, user=SNOW_USER, password=SNOW_PASS)
COMPANY_NAME = config['snow']['company']

def get_cis():
    '''Calls pysnow to query devices from SNow CMDB configuration item table.
    
    Returns:
        List[Dict[str]]: List of queried configuration items with fields as str key, value pairs
    '''
    cis = SNOW_CLIENT.resource(api_path='/table/cmdb_ci')
    query = (
        pysnow.QueryBuilder()
        .field('company.name').equals(COMPANY_NAME)
        .AND().field('name').order_ascending()
        .AND().field('u_cc_type').equals('root')
        .AND().field('u_prtg_implementation').equals('true')
        .AND().field('u_prtg_instrumentation').equals('false')
        .OR().field('u_prtg_instrumentation').is_empty()
        .AND().field('install_status').equals('1')      # Installed
        .OR().field('install_status').equals('101')     # Active
        .OR().field('install_status').equals('107')     # Duplicate installed
    )
    response = cis.get(query=query)
    return response.all()
