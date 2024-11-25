opencampusExplorer: A Blockchain Activity and Wallet Explorer
Database Definition
Database Tables
1. Blocks
Contains block-level information with the following fields:

hash: Unique identifier of the block
height: Block number in the blockchain
size: Size of the block in bytes
miner: Address of the miner/validator
difficulty: Mining difficulty
burnt_fees: Total fees burned in this block
base_fee_per_gas: Base fee per gas unit
parent_hash: Hash of the previous block
total_difficulty: Cumulative difficulty up to this block
tx_count: Number of transactions in the block
timestamp: Block creation time
gas_used: Total gas consumed
tx_fees: Total transaction fees
gas_limit: Maximum gas allowed

2. Transactions (Txs)
Stores transaction-related data with the following fields:

timestamp: Transaction execution time
fee: Transaction fee
block: Block number containing the transaction
method: Function called in the transaction
from: Sender address
tx_burnt_fee: Amount of fee burned
hash: Unique transaction identifier
priority_fee: Priority fee paid
tx_types: Transaction type
gas_used: Gas consumed by the transaction
created_contract: Address of created contract (if applicable)
to: Recipient address
result: Transaction outcome
revert_reason: Reason for reversion (if applicable)
transaction_tag: Transaction classification
has_error_in_internal_transactions: Error flag for internal transactions

3. Contracts
Contains smart contract information with the following fields:

is_vyper_contract: Vyper contract identifier
is_fully_verified: Full verification status
is_blueprint: Blueprint contract identifier
source_code: Contract source code
verified_at: Verification timestamp
is_verified: Verification status
name: Contract name
language: Programming language used
Functionality Analysis: Analysis of contract functionality
Sector and Use Classification: Contract category and usage
Identification of Potential Issues: Potential vulnerabilities
Summary and Recommendations: Analysis conclusions

4. Blocksbatch
Contains Layer 1 rollup repair transaction information with the following fields:
Open Campus-related fields:
block_heightOCS: Open Campus heigth number
batch_numberOCS: Open Campus batch number

Arbitrum-related fields:
l1_block_heightARB: Arbitrum L1 block height
batch_numberARB: Arbitrum batch number
priority_feeARB: Arbitrum priority fee
total_difficultyARB: Arbitrum total difficulty
transaction_feesARB: Arbitrum transaction fees
burnt_feesARB: Arbitrum burnt fees
difficultyARB: Arbitrum difficulty
gas_limitARB: Arbitrum gas limit
gas_usedARB: Arbitrum gas used

Ethereum-related fields:

l1_block_heightETH: Ethereum block height
total_difficultyETH: Ethereum total difficulty
transaction_feesETH: Ethereum transaction fees
burnt_feesETH: Ethereum burnt fees
difficultyETH: Ethereum difficulty
gas_limitETH: Ethereum gas limit
gas_usedETH: Ethereum gas used






