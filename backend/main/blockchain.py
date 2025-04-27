import os
import json
from django.conf import settings
from web3 import Web3

# ——— Initialization —————————————————————————————

w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))

# Load and instantiate contract
with open(settings.CONTRACT_ABI_PATH) as f:
    contract_json = json.load(f)
voting_contract = w3.eth.contract(
    address=Web3.to_checksum_address(settings.CONTRACT_ADDRESS),
    abi=contract_json['abi']
)

def default_account() -> str:
    """Return the first account from Ganache."""
    return w3.eth.accounts[0]


# ——— Helpers ——————————————————————————————————————

def get_balance(address: str) -> float:
    """
    Returns the ETH balance of `address` (in Ether).
    """
    checksum = w3.to_checksum_address(address)
    balance_wei = w3.eth.get_balance(checksum)
    return w3.from_wei(balance_wei, 'ether')


# ——— On‑chain Operations ——————————————————————————

def add_candidate_to_chain(candidate_id: int):
    """Add a candidate to the on‑chain registry."""
    acct = default_account()
    nonce = w3.eth.get_transaction_count(acct)
    tx = voting_contract.functions.addCandidate(candidate_id).build_transaction({
        'from': acct,
        'nonce': nonce,
        'chainId': w3.eth.chain_id,
        'gas': 300_000,
        'gasPrice': w3.eth.gas_price,
    })

    pk = os.getenv('PRIVATE_KEY')
    if not pk:
        raise RuntimeError("PRIVATE_KEY not set in environment")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def open_voting_on_chain():
    """Switch the contract state to open voting."""
    acct = default_account()
    nonce = w3.eth.get_transaction_count(acct)
    tx = voting_contract.functions.openVoting().build_transaction({
        'from': acct,
        'nonce': nonce,
        'chainId': w3.eth.chain_id,
        'gas': 200_000,
        'gasPrice': w3.eth.gas_price,
    })

    pk = os.getenv('PRIVATE_KEY')
    if not pk:
        raise RuntimeError("PRIVATE_KEY not set in environment")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def vote_on_chain(voter_address: str, candidate_id: int):
    """
    Cast a vote for `candidate_id` from `voter_address`.
    Raises if the account balance cannot cover the gas cost.
    """
    checksum = w3.to_checksum_address(voter_address)
    # 1) Estimate gas
    try:
        gas_est = voting_contract.functions.vote(candidate_id).estimate_gas({'from': checksum})
    except Exception as e:
        raise RuntimeError(f"Gas estimation failed: {e}")

    # 2) Compute total gas cost
    gas_price = w3.eth.gas_price
    total_cost = gas_price * gas_est

    # 3) Balance check
    balance = w3.eth.get_balance(checksum)
    if balance < total_cost:
        raise RuntimeError(
            f"Insufficient funds: balance={balance} wei, needed={total_cost} wei"
        )

    # 4) Build & sign
    nonce = w3.eth.get_transaction_count(checksum)
    tx = voting_contract.functions.vote(candidate_id).build_transaction({
        'from': checksum,
        'nonce': nonce,
        'chainId': w3.eth.chain_id,
        'gas': gas_est,
        'gasPrice': gas_price,
    })

    pk = os.getenv('PRIVATE_KEY')
    if not pk:
        raise RuntimeError("PRIVATE_KEY not set in environment")
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=pk)

    # 5) Send & wait
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def get_winner(election_id):
    # Call the getWinner function on the blockchain
    winner = voting_contract.functions.getWinner().call()
    return winner

def get_total_votes(election_id):
    # Call the getTotalVotes function on the blockchain
    total_votes = voting_contract.functions.getTotalVotes().call()
    return total_votes