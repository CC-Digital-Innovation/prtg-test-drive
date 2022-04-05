import asyncio
import logging.handlers
import re
import sys
from subprocess import CalledProcessError

from fastapi import FastAPI, HTTPException
from loguru import logger
from requests import ConnectionError, HTTPError, Timeout

from config import config
from snow import snow_api
from prtg import docker, snow_import

TOKEN = config['api']['token']
DOMAIN = config['api']['domain']
ATTEMPTS = config['api'].getint('attempts')
LOG_LEVEL = config['logger']['log_level'].upper()
SYSLOG = config['logger'].getboolean('syslog')
SYSLOG_HOST = config['logger']['syslog_host']
SYSLOG_PORT = config['logger'].getint('syslog_port')

def configure_logs():
    '''Configure logging level and syslog.'''
    # remove default logger
    logger.remove()
    if LOG_LEVEL == "QUIET":
        logger.disable(__name__)
    else:
        logger.add(sys.stderr, level=LOG_LEVEL)
        if SYSLOG:
                logger.add(logging.handlers.SysLogHandler(address = (SYSLOG_HOST, SYSLOG_PORT)))

description='''Welcome to Expert Services' PRTG demo API. Test the Expert Services experience by first clicking on the "Deploy Prtg" button below.'''

configure_logs()
with logger.catch():
    app = FastAPI(title='Expert Services - PRTG Demo API', description=description, redoc_url=None)

@app.post('/deployPrtg')
async def deploy_prtg(token: str, name: str):
    '''Start by clicking "Try it out", and enter the given token and a name for your demo. It will return a link to your demo PRTG instance. This may take a few minutes. <br />
    **These next steps is required!**<br />
    1. After your PRTG instance is created, head to the link and log in. **Immediately change your password!**<br />
    From the top naviagtion bar: **Setup > Account Settings > My Account**<br />
    2. Select on "Devices" in the top left toolbar. You will see a tree structure of monitored devices. 
    Right click on "Local Probe" and select "Add Device...". Put "demo" for the required "IPv4 Address/DNS Name" field. 
    Now you're ready to import the devices from SNOW CMDB!
    \f
    Creates demo PRTG instance inside Docker with fake devices.
    Note: Order of creating PRTG and device containers matter. The PRTG docker-compose file creates
    a PRTG network first and then the device docker-compose file adds the devices to that network.

    Args:
        token (str): A secret token.
        name (str): A name for the demo PRTG instance. It must be a valid subdomain name, i.e. it must
            start and end with an alphanumeric character and cannot have spaces or specials chatacters,
            except '-' (hyphen/minus symbol).
    '''
    logger.info('------------------------------------------------------------')
    logger.info('Starting Demo PRTG Deployment.')
    if token != TOKEN:
        logger.warning('Unauthorized attempt made.')
        raise HTTPException(status_code=401)
    
    # Validate input is a valid subdomain name
    if not re.fullmatch('[A-Za-z0-9](?:[A-Za-z0-9\-]{0,61}[A-Za-z0-9])?', name):
        raise HTTPException(status_code=400, 
                            detail='Name must start and end with an alphanumeric character and cannot have spaces or special characters, except \'-\' (hyphen/minus symbol).')

    # Check if name is already in use
    if docker.name_exists(name):
        raise HTTPException(status_code=400, detail='Name is already in use.')

    # Call function to start up PRTG contianer
    # Call function to create DNS entry for PRTG container
        # Currently implemented using caddy labels in docker-compose file
    logger.debug(f'Creating PRTG container "{name}"...')
    try:
        docker.deploy_prtg(name)
    except CalledProcessError as e:
        logger.error(e)
        logger.debug('Removing PRTG container and network if it exists...')
        docker.remove_prtg(name)
        raise HTTPException(status_code=500)
    logger.info(f'PRTG container "{name}" created.')
    
    # Call function to deploy two fake devices that map to SNOW CMDB
    logger.debug('Getting SNOW devices...')
    try:
        devices = snow_api.get_cis()
    except (ConnectionError, HTTPError, Timeout) as e:
        logger.error(e)
        logger.debug('Removing PRTG container and network...')
        docker.remove_prtg(name)
        raise HTTPException(status_code=500)
    logger.debug('Creating devices from SNOW...')
    try:
        for device in devices:
            if not device['ip_address'] and not device['u_host_name']:
                logger.warning(f'Skipping {device["name"]} because it is missing both a host name and IP address.')
                continue
            logger.debug(f'Creating device "{device["name"]}"...')
            docker.deploy_device(name, device['ip_address'], device['u_host_name'])
            logger.debug(f'Device "{device["name"]}" created.')
    except CalledProcessError as e:
        logger.error(e)
        logger.debug('Removing device containers if it exists...')
        for device in devices:
            docker.remove_devices(name, device['ip_address'], device['u_host_name'])
        logger.debug('Removing PRTG container and network...')
        docker.remove_prtg(name)
        raise HTTPException(status_code=500)
    logger.info(f'{len(devices)} device containers created.')

    # Wait for PRTG instance to be ready
    # TODO implement better way to actually know when it's done
    logger.info('Waiting for PRTG to initialize...')
    await asyncio.sleep(60)
    logger.info('PRTG Initialized!')

    # Call api to build the PRTG build process
    url = f'https://{name.lower()}.{DOMAIN}'
    
    logger.info(f'Successfully deployed PRTG instance \'{name}\' at {url}.')
    return f'Successfully deployed PRTG instance \'{name}\' at {url}'

@app.post('/importSnow')
async def import_from_snow(token: str, name: str):
    '''**Complete the "Deploy PRTG" step before you begin this one!**<br />
    Use the same name from the previous step and the token into the fields. Select "Execute" and head back to your PRTG instance.
    Watch as the devices begin to populate. When this step is done, you can right click on the new devices and select "Run Auto-Discovery".
    \f
    Call XSAutomate API to initialize the new PRTG instance from SNOW CMDB. 

    Args:
        token (str): A secret token.
        name (str): Name of PRTG Test Drive used in deploy_prtg()
    '''
    logger.info('------------------------------------------------------------')
    logger.info('Using XSAutomate API to import from SNOW CMDB...')
    if token != TOKEN:
        logger.warning('Unauthorized attempt made.')
        raise HTTPException(status_code=401)

    # Check if PRTG Test Drive was created.
    if not docker.name_exists(name):
        raise HTTPException(status_code=400, detail=f'Cannot find PRTG Test Drive with name: \'{name}\'.')

    url = f'https://{name.lower()}.{DOMAIN}'

    for i in range(1, ATTEMPTS + 1):
        try:
            snow_import.init_prtg(url)
            break
        except (ConnectionError, HTTPError, Timeout) as e:
            if i < ATTEMPTS:
                logger.warning(f'Could not reach XSAutoamte API. ({i}) Trying again...')
                await asyncio.sleep(5)
                continue
            logger.error(e)
            raise HTTPException(status_code=500)

    # Remove PRTG container from API network
    docker.disconnect_from_network(name)

    logger.info('Successfully imported from SNOW CMDB to PRTG.')
    return f'Successfully imported from SNOW CMDB to PRTG. Try running Auto-Discovery on the devices to see what sensors it recommends!'

# NOTE dev purposes only
@app.delete('/dev/prtg/{name}', include_in_schema=False)
async def delete_prtg(name: str, dev_token: str):
    '''Deletes demo PRTG instance containers based on name.
    Note: Order of deleting PRTG instance and device containers matter. The device docker-compose file
    uses the network created from the PRTG docker-compose file. Removing the PRTG and its network first
    will result in an error.

    Args:
        name (str): name of the demo PRTG instance.
    '''
    logger.info('------------------------------------------------------------')
    logger.info('Deleting Demo PRTG Deployment.')

    if dev_token != TOKEN:
        logger.warning('Unauthorized attempt made.')
        raise HTTPException(status_code=401)

    logger.debug('Getting SNOW devices...')
    try:
        devices = snow_api.get_cis()
    except (ConnectionError, HTTPError, Timeout) as e:
        logger.error('Failed to retrieve SNOW devices.')
        logger.error(e)
        raise HTTPException(status_code=500)

    logger.debug('Removing device containers.')
    for device in devices:
        logger.debug(f'Removing device {device["name"]} if it exists...')
        docker.remove_devices(name, device['ip_address'], device['u_host_name'])

    logger.debug('Removing PRTG container and network if it exists...')
    docker.remove_prtg(name)

    logger.info(f'Successfully deleted PRTG instance \'{name}\'.')
    return f'Successfully deleted PRTG instance \'{name}\'.'
