from web3 import Web3

# Connect to your local Ganache instance
ganache_url = "http://192.168.0.146:8545"  # Update this if your Ganache is running on a different host or port
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Verify connection
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Ganache at {}".format(ganache_url))

# Replace with the address you want to check
address = "0x92aD16E43a5F487794515EAB4589A0c93c689585"

# Ensure the address is checksummed
checksum_address = w3.to_checksum_address(address)

# Retrieve balance
balance_wei = w3.eth.get_balance(checksum_address)

# Convert balance from Wei to Ether
balance_eth = w3.from_wei(balance_wei, 'ether')

print(f"Balance of {checksum_address}: {balance_eth} ETH")
