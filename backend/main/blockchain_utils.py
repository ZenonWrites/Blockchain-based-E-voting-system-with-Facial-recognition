import hashlib
import json
from datetime import datetime
from main.models import BlockchainTransaction

def add_user_to_blockchain(user):
    # Construct the data for the transaction
    transaction_data = {
        "event": "User Registered",
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "wallet_address": user.wallet_address,
        "voter_id": user.voter_id,
        "timestamp": str(datetime.utcnow())
    }

    # Create a hash of the data
    data_string = json.dumps(transaction_data, sort_keys=True).encode()
    transaction_hash = hashlib.sha256(data_string).hexdigest()

    # Save to BlockchainTransaction model
    BlockchainTransaction.objects.create(
        user=user,
        transaction_type="registration",
        data=json.dumps(transaction_data),
        hash=transaction_hash
    )
