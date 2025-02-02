# -*- coding: utf-8 -*-

from configparser import ConfigParser 
from pydal import DAL
import os

configuration = ConfigParser()
configuration.read('private/appconfig.ini')

pwd = os.getcwd()
try:
    os.stat(pwd + configuration.get('db','folder'))
except:
    os.mkdir(pwd + configuration.get('db','folder'))

db = DAL(configuration.get('db','uri'),
            pool_size=configuration.get('db','pool_size'),
            migrate_enabled=configuration.get('db','migrate'),
            folder=configuration.get('db','folder')
        )
url_api_educhain="https://educhain.blockscout.com/"
url_api_arbitrum="https://arbitrum.blockscout.com/"
url_api_ethereum="https://eth.blockscout.com/"
recaptcha_site_key = configuration.get('recaptcha','site_key')
recaptcha_secret_key = configuration.get('recaptcha','secret_key')