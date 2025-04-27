from django.http import JsonResponse
from web3 import Web3
import json
from .models import VerificationRequest

# Setup Web3 connection - replace with your Ganache URL
ganache_url = "http://192.168.0.146:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

# Default account for transactions
web3.eth.defaultAccount = web3.eth.accounts[0]

# Load contract ABI and address - replace with your contract details
with open('../build/contracts/IdentityVerification.json', 'r') as f:
    contract_abi = json.load(f)
contract_address = '0x28Fc09C00a32fD04734cA0e7E455f6409530DD76'  # Replace with your deployed contract address
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def record_verification_on_blockchain(request):
    verification_id = request.session.get('verification_id')
    
    if not verification_id:
        return JsonResponse({
            'status': 'error',
            'message': 'No verification session found'
        }, status=404)
    
    try:
        verification = VerificationRequest.objects.get(id=verification_id)
        
        # Only record verified users
        if verification.status != 'verified':
            return JsonResponse({
                'status': 'error',
                'message': 'User not verified'
            }, status=400)
        
        # Call the smart contract function
        tx_hash = contract.functions.verifyUser(str(verification.id)).transact()
        
        # Wait for transaction receipt
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Verification recorded on blockchain',
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt['blockNumber']
        })
    
    except VerificationRequest.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Verification request not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Blockchain error: {str(e)}'
        }, status=500)