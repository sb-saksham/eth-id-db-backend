import json
from pathlib import Path

from django.conf import settings

from web3.exceptions import ContractLogicError
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

with open(str(Path.joinpath(settings.BASE_DIR, "web3op/IdDb.json"))) as IdDbContractFile:
    IdDbContract = json.loads(IdDbContractFile.read())

alchemy_url = f"https://eth-sepolia.g.alchemy.com/v2/{settings.ALCHEMY_KEY}"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# noinspection PyTypeChecker
id_db_contract = w3.eth.contract(
    address=settings.CONTRACT_ADDRESS,
    abi=IdDbContract['abi']
)
private_key = settings.OWNER_PRIVATE_KEY

assert private_key is not None, "You must set PRIVATE_KEY environment variable"
assert private_key.startswith("0x"), "Private key must start with 0x hex prefix"
account: LocalAccount = Account.from_key(private_key)
w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
w3.eth.default_account = account.address


def set_verified_on_bc(ens, full_name):
    try:
        verified_domain = id_db_contract.functions.verifiedDomains(ens).call()
        if not verified_domain:
            transaction = id_db_contract.functions.verify(ens, full_name).transact()
            tx_receipt = w3.eth.wait_for_transaction_receipt(transaction)
            print(tx_receipt)
    except ContractLogicError as c:
        print("data ", c.message)


set_verified_on_bc("Saksham", "SB DON")
