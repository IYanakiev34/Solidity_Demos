from itertools import chain
from solcx import compile_standard, install_solc

install_solc("0.6.0")
import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# Compile solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            },
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)


# get bytecode

bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]


# get abi

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://172.31.16.1:7000"))
chain_id = 1337
my_address = "0xe600e2112250c73edE5145c66460946D3a41C81f"
# when adding private key we need to add the 0x since we need the hexadecimal version
# never add private key in code generally
private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

nonce = w3.eth.getTransactionCount(my_address)

# 1.Build Transaction
# 2.Sign Transaction
# 3.Send Transaction

transaction = SimpleStorage.constructor().buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce,
    }
)

signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)

# deploying the contract
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_reciept = w3.eth.wait_for_transaction_receipt(tx_hash)

# Working with the contract we always need,
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address=tx_reciept.contractAddress, abi=abi)

# Call -> Simulate making the call without changing state
# Transact -> Actually make state change

# Initial value of favorite number
print(simple_storage.functions.retrieve().call())

# Same steps as above

# Create transaction
store_stransaction = simple_storage.functions.store(15).buildTransaction(
    {
        "chainId": chain_id,
        "gasPrice": w3.eth.gas_price,
        "from": my_address,
        "nonce": nonce + 1,
    }
)

# Sign transaction
signed_store_tx = w3.eth.account.sign_transaction(
    store_stransaction, private_key=private_key
)

# Send transaction
send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)

# Get the reciept
tx_reciept = w3.eth.wait_for_transaction_receipt(send_store_tx)

print(simple_storage.functions.retrieve().call())
