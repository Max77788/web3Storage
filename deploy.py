from solcx import compile_standard, install_solc

import json

from web3 import Web3

from SECRETS import PRIVATE_KEY

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    #print(simple_storage_file)

# We add these two lines that we forgot from the video!
install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to Goerli

w3 = Web3(Web3.HTTPProvider("https://goerli.infura.io/v3/d3985fcee116489fae9c8fee5e6fedbc"))
chain_id = 5
my_address = "0xD8090a772c153ae4AD71fc51C82A00fa7a48d18c"
private_key = PRIVATE_KEY

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.get_transaction_count(my_address)
#print(nonce)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().build_transaction({"chainId":chain_id, "from":my_address, "nonce":nonce})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# Send this signed transaction
print("Deploying contract...\n")
tx_hash =  w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Deployed!\n")
# Working with the contract, you always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change

# Initial value of favorite number
print("Retrieving value before any state change...\n")
print(simple_storage.functions.retrieve().call()) 

print("Changing favorite number...\n")
store_transaction = simple_storage.functions.store(15).build_transaction({
    "chainId": chain_id, "from": my_address, "nonce": nonce + 1
}) 
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Change completed!\n")

print("New value:")
print(simple_storage.functions.retrieve().call()) 