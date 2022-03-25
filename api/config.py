import configparser
from pathlib import PurePath

config = configparser.ConfigParser()
config_path = PurePath(__file__).parent/'config.ini'
with open(config_path) as f:
    config.read_file(f)
