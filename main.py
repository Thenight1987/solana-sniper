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

# For Telegram integration
from telethon import TelegramClient, events, errors

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

# Main Telegram listener function
def Telegram():
    # Set your Telegram credentials
    session_name = "solana_sniper_session"  # Make sure your session name is correct
    api_id = 123456  # Replace with your actual API ID from Telegram
    api_hash = "your_telegram_api_hash"  # Replace with your actual API Hash

    with TelegramClient(session_name, api_id, api_hash) as client:
        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            print_message("Message Received")
            channel_check = event.is_channel
            if channel_check:
                sender_username = event.message._sender.username
                # Make sure you are monitoring the correct users
                sender_usernames = ['user1', 'user2']  # Add the usernames you want to monitor
                for user in sender_usernames:
                    if user == sender_username:
                        message_received = event.message.message
                        if message_received:
                            channel_id = event.chat_id
                            sender_id = event.message.sender_id
                            token_address = None
                            # Check for different token patterns in the message
                            birdeye_pattern = r'https?://birdeye\.so/token/(\w+)\?chain=solana'
                            dex_pattern = r'https://dexscreener\.com/solana/(\w+)'

                            birdeye_url = re.search(birdeye_pattern, message_received)
                            dex_url = re.search(dex_pattern, message_received)
                            if birdeye_url:
                                token_address = birdeye_url.group(1)
                            elif dex_url:
                                token_address = dex_url.group(1)

                            if token_address:
                                logging_info(token_address, sender_username, channel_id, message_received)
                                # Call the trade function in a new thread
                                Thread(target=select_amm2trade, name=token_address, args=(token_address, payer, ctx)).start()

        # Run the client
        client.run_until_disconnected()

# Run the Telegram listener
if __name__ == "__main__":
    try:
        Telegram()
    except errors.FloodWaitError as e:
        print(f'Have to sleep {e.seconds} seconds')
        time.sleep(e.seconds)
    except Exception as e:
        logging.error(f"Exception in Telegram Client: {e}")
        print("Exception in Telegram Client:", e)
