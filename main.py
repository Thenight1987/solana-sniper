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

# Initialize logging
logging.basicConfig(level=logging.DEBUG)  # Logs all debug-level messages

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
    logging.debug(f"{formatted_date_time} | {message}")

def logging_info(token_address, author, channel_id, message_received):
    # Logging token and message information
    logging.info(f"Message received {token_address} --->\n"
                 f"Username: {author}\nChannel: {channel_id}\n"
                 f"Message: {message_received}\n"
                 f"Pair Address: https://birdeye.so/token/{token_address}?chain=solana\n"
                 "-------------------------------------------------")
    # Assuming sendWebhook function exists
    sendWebhook(f"msg|Token Found", f"------------------------------\nMessage received\n"
                                   f"Username: {author}\nChannel: {channel_id}\nMessage: {message_received}\n"
                                   f"Pair Address: https://birdeye.so/token/{token_address}?chain=solana")

# Main function to monitor token drops
def monitor_token_drops():
    logging.debug("Starting to monitor tokens.")
    # Load previous tokens
    file_path = os.path.join(sys.path[0], 'data', 'previousSELLBUYINFO.json')
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        logging.debug(f"Loaded {len(data)} tokens from previousSELLBUYINFO.json.")

        if len(data) > 0:
            for token in data:
                # Call select_amm2trade token method.
                logging.debug(f"Processing token: {token}")
                Thread(target=select_amm2trade, name=token, args=(token, payer, ctx)).start()
    except Exception as e:
        logging.error(f"Error loading or processing tokens: {e}")

def main():
    logging.debug("Bot started, beginning token monitoring...")
    try:
        monitor_token_drops()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        print("Error occurred:", e)

if __name__ == "__main__":
    logging.debug("Main execution started.")
    main()
