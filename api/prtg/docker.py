import os
import subprocess
from pathlib import PurePath

from config import config

MODULE_DIR = PurePath(__file__).parent
DOMAIN = config['api']['domain']

def deploy_prtg(name: str):
    '''Calls subprocess to deploy PRTG container in host Docker.

    Args:
        name (str): Name of the test drive
    
    Raises:
        subprocess.CalledProcessError if subprocess returned non-zero code
    '''
    name = name.strip().lower()
    subprocess.run(['docker-compose', '-p', name, '-f', MODULE_DIR/'prtg-compose.yml', 'up', '-d'], env=dict(SUBDOMAIN=name, DOMAIN=DOMAIN, **os.environ), check=True)

def deploy_device(name: str, ip_addr: str, hostname: str):
    '''Calls subprocess to deploy test device container in host Docker.

    Args:
        name (str): Name of the test drive
        ip_addr (str): IP address of device
        hostname (str): Hostname of device
    
    Raises:
        subprocess.CalledProcessError if subprocess returned non-zero code
    '''
    name = name.strip().lower()
    subprocess.run(['docker-compose', '-p', f'{name}-{hostname}', '-f', MODULE_DIR/'device-compose.yml', 'up', '-d'],
                    env=dict(PRTG_NAME=name, DEV_IP_ADDR=ip_addr, DEV_HOST=hostname, **os.environ), check=True)

def remove_prtg(name: str):
    '''Calls subprocess to delete PRTG container in host Docker.

    Args:
        name (str): Name of the test drive
    
    Raises:
        subprocess.CalledProcessError if subprocess returned non-zero code
    '''
    name = name.strip().lower()
    subprocess.run(['docker-compose', '-p', name, '-f', MODULE_DIR/'prtg-compose.yml', 'down'], env=dict(SUBDOMAIN=name, DOMAIN=DOMAIN, **os.environ), check=True)

def remove_devices(name: str, ip_addr: str, hostname: str):
    '''Calls subprocess to delete test device container in host Docker.

    Args:
        name (str): Name of the test drive
        ip_addr (str): IP address of device
        hostname (str): Hostname of device
    
    Raises:
        subprocess.CalledProcessError if subprocess returned non-zero code
    '''
    name = name.strip().lower()
    subprocess.run(['docker-compose', '-p', f'{name}-{hostname}', '-f', MODULE_DIR/'device-compose.yml', 'down'], 
                    env=dict(PRTG_NAME=name, DEV_IP_ADDR=ip_addr, DEV_HOST=hostname, **os.environ), check=True)

def name_exists(name: str):
    '''Calls subprocess to filter for project name.

    Args:
        name (str): Name of the test drive

    Returns:
        bool: if name exists

    Raises:
        subprocess.CalledProcessError if subprocess returned non-zero code
    '''
    return bool(subprocess.run(['docker', 'ps', '-a', '--format', '"{{.Names}}"', '--filter', f'name=^{name.strip().lower()}.*$'], text=True, check=True, capture_output=True).stdout)
