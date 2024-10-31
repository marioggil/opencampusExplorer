from pydal import DAL, Field
from config.parameters import db
import datetime


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