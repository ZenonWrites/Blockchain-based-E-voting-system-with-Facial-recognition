# main/VotingResult.py

import json
from pathlib import Path

from django.conf import settings
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput
from .models import VotingResult, Election, Candidate
from dotenv import load_dotenv
import os

load_dotenv()

# ─── Load contract ABI & address once ─────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent.parent
CONTRACT_JSON_PATH = BASE_DIR / 'build' / 'contracts' / 'VotingContract.json'
with open(CONTRACT_JSON_PATH) as f:
    contract_data = json.load(f)

VOTING_CONTRACT_ABI     = contract_data['abi']
CONTRACT_ADDRESS = os.getenv('VOTING_CONTRACT_ADDRESS')


def get_voting_result(election_id):
    """
    1) Connect to Web3
    2) Verify contract is deployed
    3) Instantiate contract
    4) Load election & its Candidate objects
    5) Call on-chain getWinner() → returns index into that Candidate list
    6) Map index → Candidate instance
    7) Tally votes for each candidate index
    8) Persist & return VotingResult
    """

    # 1) Connect
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
    if not w3.is_connected():
        raise RuntimeError(f"Cannot connect to {settings.WEB3_PROVIDER_URI}")

    # 2) Verify contract bytecode
    checksum_addr = Web3.to_checksum_address(CONTRACT_ADDRESS)
    code = w3.eth.get_code(checksum_addr)
    if code in (b'', b'0x', '0x'):
        raise RuntimeError(f"No contract deployed at {checksum_addr}")

    # 3) Instantiate
    contract = w3.eth.contract(address=checksum_addr, abi=VOTING_CONTRACT_ABI)

    # 4) Load election and its Candidate objects (not CustomUser!)
    election   = Election.objects.get(id=election_id)
    candidates = list(Candidate.objects.filter(election=election))  # ← use the Candidate model

    # 5) On-chain call
    try:
        winner_index = contract.functions.getWinner().call({'from': w3.eth.accounts[0]})
    except BadFunctionCallOutput as e:
        raise RuntimeError(f"Error calling getWinner(): {e}")

    # 6) Map to Candidate
    if not (0 <= winner_index < len(candidates)):
        raise RuntimeError(f"Winner index {winner_index} out of range")
    winner_candidate = candidates[winner_index]

    # 7) Tally votes
    total_votes = 0
    for idx, cand in enumerate(candidates):
        try:
            votes = contract.functions.candidateVotes(idx).call({'from': w3.eth.accounts[0]})
        except BadFunctionCallOutput:
            votes = 0
        total_votes += votes

    # 8) Persist and return
    return VotingResult.objects.create(
        election=election,
        winner=winner_candidate,    # now a Candidate instance
        total_votes=total_votes
    )
