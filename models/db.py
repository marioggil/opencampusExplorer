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
                Field('is_vyper_contract'),
                Field('is_fully_verified'),
                Field('is_blueprint'),
                Field('source_code'),
                Field('verified_at'),
                Field('is_verified'),
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
Field('is_contract'),#Buscable
Field('orcid'),#Buscable #secreto
Field('telegram'), #secreto
Field('last_login'),
Field('count_login'),
Field('wallet_id'),
Field('created_on','datetime',default=datetime.datetime.now())
)
db.define_table("txs",
  Field('timestamp'),#Buscable
  Field('fee'),
  Field('block',type="integer"),#Buscable
  Field('method'),
  Field('tx_burnt_fee'),
  Field('hash'),#Buscable
  Field('priority_fee'),
  Field('tx_types'),
  Field('gas_used'),
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
Field('size'),# integer
Field('miner'),
Field('difficulty'),#  integer
Field('burnt_fees'),#  integer
Field('base_fee_per_gas'),#  integer
Field('parent_hash'),
Field('total_difficulty'),#  integer
Field('tx_count'),#  integer
Field('timestamp'),#Buscable
Field('gas_used'),#  integer
Field('tx_fees'),#  integer
Field('gas_limit'),#  integer
)


db.define_table("blocksbach",
Field('block_heightOCS',type="integer"), # integer
Field('batch_numberOCS',type="integer"), # integer
Field('l1_block_heightARB'),#  integer
Field('batch_numberARB'),#  integer
Field('priority_feeARB'), # integer
Field('total_difficultyARB'),#  integer
Field('transaction_feesARB'), # integer
Field('burnt_feesARB'),#  integer
Field('difficultyARB'),#  integer
Field('gas_limitARB'),#  integer
Field('gas_usedARB'),#  integer
Field('l1_block_heightETH'), # integer
Field('total_difficultyETH'),#  integer
Field('transaction_feesETH'), # integer
Field('difficultyETH'),#  integer
Field('gas_limitETH'),#  integer
Field('gas_usedETH'), # integer
Field('block_hashOCS')
)

db.define_table("errors",
                Field('table'),
                Field('hash'),
                Field('block')
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

