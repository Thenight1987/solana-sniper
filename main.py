import base58
import logging
import time
import re
import os
import sys
import json
from datetime import datetime
from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
import threading

# Custom methods (make sure these are in place)
from amm_selection import select_amm2trade
from webhook import sendWebhook

# Initialize logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for detailed logs

# Set your private key directly here (replace with your private key)
PRIVATE_KEY = "435paW8T84RXzpv7hDJV2a2akihe8QGqPfLQG7qHZNtxqAaE1E8jgouKt5EyoMjgMdkA2h2kXwGQaTREZwXh37uq"
payer = Keypair.from_bytes(base58.b58decode(PRIVATE_KEY))

# Solana RPC URL (using mainnet)
RPC_HTTPS_URL = "https://api.mainnet-beta.solana.com"

# Solana Client Initialization
ctx = Client(RPC_HTTPS_URL, commitment=Commitment("confirmed"), timeout=30, blockhash_cache=True)

# Function to log messages
def print_message(message):
    now = datetime.now()
    formatted_date_time = now.strftime("%d/%m/%Y|%I:%M %p")
    print(f"{formatted_date_time} | {message}")

def logging_info(token_address, author, channel_id, message_received):
    # Logging token and message information
    logging.info(f"Message received {token_address} --->\n"
                 f"Username: {author}\nChannel: {channel_id}\n"
                 f"Message: {message_received}\n"
                 f"Pair Address: https://birdeye.so/token/{token_address}?chain=solana\n"
                 "-------------------------------------------------")
    sendWebhook(f"msg|Token Found", f"------------------------------\nMessage received\n"
                                   f"Username: {author}\nChannel: {channel_id}\nMessage: {message_received}\n"
                                   f"Pair Address: https://birdeye.so/token/{token_address}?chain=solana")

# Main function to monitor token drops
def monitor_token_drops():
    # Load previous tokens
    file_path = os.path.join(sys.path[0], 'data', 'previousSELLBUYINFO.json')
    with open(file_path, 'r') as file:
        data = json.load(file)

    if len(data) > 0:
        for token in data:
            # Call select_amm2trade token method.
            Thread(target=select_amm2trade, name=token, args=(token, payer, ctx)).start()

def main():
    # Run the bot
    try:
        monitor_token_drops()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        print("Error occurred:", e)

if __name__ == "__main__":
    main()
