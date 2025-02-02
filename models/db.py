from pydal import DAL, Field
from config.parameters import db
import datetime




# db.define_table('datas',
#                 Field('wallet','reference wallets'),
#                 Field('uuid'),
#                 Field('url'),
#                 Field('color'),
#                 Field('source'),
#                 Field('target'),
#                 Field('width'),
#                 Field('created_on','datetime',default=datetime.datetime.now())
#                 )


db.define_table("contracts",
                Field('hash'),#Buscable
                Field('is_vyper_contract',type="boolean"),
                Field('is_fully_verified',type="boolean"),
                Field('is_blueprint',type="boolean"),
                Field('source_code'),
                Field('verified_at'),
                Field('is_verified',type="boolean"),
                Field('name'),
                Field('language'),
                Field('compiler_version'),
                Field('evm_version'),
                Field('functionality'),
                Field('sectoruse'),
                Field('issues'),
                Field('summary')
)

db.define_table("wallets",
Field('hash'),#Buscable
Field('is_contract',type="integer"),#Buscable
Field('orcid'),#Buscable #secreto
Field('telegram'), #secreto
Field('last_login',type="datetime"),
Field('count_login',type="integer"),
Field('wallet_id'),
Field('created_on','datetime',default=datetime.datetime.now())
)
db.define_table("txs",
  Field('timestamp',type="datetime",represent=lambda value, row: value.strftime('%Y-%m-%d %H:%M:%S') if value else ''),#Buscable
  Field('day_week'),  # Nombre del día
  Field('day_month',type="integer"),  # Día del mes como número
  Field('hour',type="integer") , # Hora en formato 24h
  Field('fee',type="integer"),
  Field('block',type="integer"),#Buscable
  Field('method'),
  Field('tx_burnt_fee',type="integer"),
  Field('hash'),#Buscable
  Field('priority_fee',type="integer"),
  Field('tx_types'),
  Field('gas_used',type="integer"),
  Field('created_contract'),
  Field('result'),
  Field('revert_reason'),
  Field('transaction_tag'),
  Field('has_error_in_internal_transactions'),
  Field('fromw'),#Buscable
  Field('tow'),#Buscable
)


db.define_table("blocks",
Field('hash'),#Buscable
Field('height',type="integer"),#Buscable # integer 
Field('size',type="integer"),# integer
Field('miner'),
Field('difficulty',type="integer"),#  integer
Field('burnt_fees',type="integer"),#  integer
Field('base_fee_per_gas',type="integer"),#  integer
Field('parent_hash'),
Field('total_difficulty',type="integer"),#  integer
Field('tx_count',type="integer"),#  integer
Field('timestamp',type="datetime",represent=lambda value, row: value.strftime('%Y-%m-%d %H:%M:%S') if value else ''),#Buscable
Field('gas_used',type="integer"),#  integer
Field('tx_fees',type="integer"),#  integer
Field('gas_limit',type="integer"),#  integer
Field('day_week'),  # Nombre del día
Field('day_month',type="integer"),  # Día del mes como número
Field('hour',type="integer")  # Hora en formato 24h
)

db.define_table("blocksbach",
Field('block_heightOCS',type="integer"), # integer
Field('batch_numberOCS',type="integer"), # integer
Field('l1_block_heightARB',type="integer"),#  integer
Field('batch_numberARB',type="integer"),#  integer
Field('priority_feeARB',type="integer"), # integer
Field('total_difficultyARB',type="integer"),#  integer
Field('transaction_feesARB',type="integer"), # integer
Field('burnt_feesARB',type="integer"),#  integer
Field('difficultyARB',type="integer"),#  integer
Field('gas_limitARB',type="integer"),#  integer
Field('gas_usedARB',type="integer"),#  integer
Field('l1_block_heightETH',type="integer"), # integer
Field('total_difficultyETH',type="integer"),#  integer
Field('transaction_feesETH',type="integer"), # integer
Field('difficultyETH',type="integer"),#  integer
Field('gas_limitETH',type="integer"),#  integer
Field('gas_usedETH',type="integer"), # integer
Field('block_hashOCS',type="integer")
)

db.define_table("errors",
                Field('created_on','datetime',default=datetime.datetime.now()),
                Field('table'),
                Field('hash'),
                Field('block')
)

db.define_table("stadists_site",
                Field('created_on','datetime',default=datetime.datetime.now()),
                Field('n_wallets',type="integer"),
                Field('n_contracts',type="integer"),
                Field('n_contracts_is_vyper_contract',type="integer"),
                Field('n_contracts_is_verified',type="integer"),
                Field('n_contracts_language'),
                Field('n_contracts_evm_version'),
                Field('n_txs',type="integer"),
                Field('n_txs_not_success',type="integer"),
                Field('n_blocks',type="integer"),
                Field('n_blocks_tx_count'),
                Field('n_blocks_miner'),
                
)



db.executesql('CREATE INDEX IF NOT EXISTS hash_finder_contract ON contracts(hash);')
db.executesql('CREATE INDEX IF NOT EXISTS hash_finder_wallet ON wallets(hash);')
db.executesql('CREATE INDEX IF NOT EXISTS is_contract_finder_wallet ON wallets(is_contract);')
db.executesql('CREATE INDEX IF NOT EXISTS orcid_finder_wallet ON wallets(orcid);')
db.executesql('CREATE INDEX IF NOT EXISTS timestamp_finder_tx ON txs(timestamp);')
db.executesql('CREATE INDEX IF NOT EXISTS block_finder_tx ON txs(block);')
db.executesql('CREATE INDEX IF NOT EXISTS hash_finder_tx ON txs(hash);')
db.executesql('CREATE INDEX IF NOT EXISTS fromw_finder_tx ON txs(fromw);')
db.executesql('CREATE INDEX IF NOT EXISTS tow_finder_tx ON txs(tow);')
db.executesql('CREATE INDEX IF NOT EXISTS timestamp_finder_block ON blocks(timestamp);')
db.executesql('CREATE INDEX IF NOT EXISTS height_finder_block ON blocks(height);')
db.executesql('CREATE INDEX IF NOT EXISTS hash_finder_block ON blocks(hash);')
db.executesql('CREATE INDEX IF NOT EXISTS block_finder_blocksbach ON blocksbach(block_hashOCS);')

