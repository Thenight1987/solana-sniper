import base58
import logging
import time
import os
import sys
from datetime import datetime
from solders.keypair import Keypair
from solana.rpc.api import Client
from solana.rpc.commitment import Commitment
import threading

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

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
    logging.info(f"New token found: {token_address} --->\n"
                 f"Message: {message_received}\n"
                 f"Pair Address: https://birdeye.so/token/{token_address}?chain=solana\n"
                 "-------------------------------------------------")
    # Assuming sendWebhook function exists to notify about new token
    sendWebhook(f"msg|Token Found", f"Token found!\nMessage: {message_received}\nPair Address: {token_address}")

# Main function to continuously check for new tokens
def monitor_new_tokens():
    logging.debug("Starting to monitor for new tokens.")

    # Example: Listening for new token pairs on Raydium (You can modify this for other DEXes)
    while True:
        try:
            # This is just an example; you can implement actual logic to watch for new token pairs
            # For example, check new trades or liquidity pool creations on Raydium, Jupiter, or Orca.

            # Example new token detected (replace with actual logic for getting new tokens)
            new_token = "NewTokenAddress"
            print_message(f"Found new token: {new_token}")
            logging_info(new_token, "Bot", "Channel ID", f"New token detected: {new_token}")

            # Trigger sniping or other actions based on your strategy
            Thread(target=select_amm2trade, name=new_token, args=(new_token, payer, ctx)).start()
            time.sleep(5)  # Adjust as needed for delay between checks

        except Exception as e:
            logging.error(f"Error while monitoring new tokens: {e}")
            time.sleep(5)

def main():
    logging.debug("Bot started, beginning to monitor for new tokens...")
    try:
        monitor_new_tokens()
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        print("Error occurred:", e)

if __name__ == "__main__":
    main()
