from pydal import DAL, Field

import os, datetime

pwd = os.getcwd()
try:
    os.stat(pwd + '/databases')
except:
    os.mkdir(pwd + '/databases')
    
db = DAL("sqlite://storage.sqlite",
            pool_size=10,
            migrate_enabled=True,
            folder="databases"
        )

db.define_table('wallets',
                Field('wallet_id'),
                Field('created_on','datetime',default=datetime.datetime.now())
                )

db.define_table('datas',
                Field('wallet','reference wallets'),
                Field('uuid'),
                Field('url'),
                Field('color'),
                Field('source'),
                Field('target'),
                Field('width'),
                Field('created_on','datetime',default=datetime.datetime.now())
                )