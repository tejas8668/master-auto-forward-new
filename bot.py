from pyrogram import Client, filters
import asyncio
import logging
import os
from dotenv import load_dotenv
import json

load_dotenv('config.env', override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_SESSION = os.getenv("USER_SESSION")

# Load channel mappings from the JSON file
with open("chat_list.json", "r") as json_file:
    CHANNEL_MAPPING = json.load(json_file)

# Initialize the Client with user session or bot token
if USER_SESSION:
    app = Client(
        "my_user_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=USER_SESSION,
    )
    logger.info("Bot started using Session String")
else:
    app = Client(
        "my_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    logger.info("Bot started using Bot Token")

async def check_channel_access():
    try:
        for mapping in CHANNEL_MAPPING:
            source_channel = int(mapping["source"])
            channel = await app.get_chat(source_channel)
            logger.info(f"Access to source channel {source_channel}: {channel.title}")
    except Exception as e:
        logger.error(f"Error accessing source channel: {e}")
        raise

@app.on_message(filters.channel)
async def forward(client, message):
    try:
        for mapping in CHANNEL_MAPPING:
            source_channel = mapping["source"]
            destinations = mapping["destinations"]

            if message.chat.id == int(source_channel):
                for destination in destinations:
                    try:
                        # Forward the message as-is
                        await client.forward_messages(chat_id=int(destination), from_chat_id=message.chat.id, message_ids=message.id)
                        logger.info(f"Forwarded message ID {message.id} from {source_channel} to {destination}")
                        await asyncio.sleep(5)
                    except Exception as e:
                        logger.error(f"Error forwarding message {message.id} to {destination}: {e}")
                        raise
                await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in forwarding process: {e}")
        raise

async def manage_connection():
    try:
        if app.is_connected:
            logger.info("Client is already connected, disconnecting...")
            await app.disconnect()
        logger.info("Connecting client...")
        await app.connect()
        await check_channel_access()
    except Exception as e:
        logger.error(f"Error in managing connection: {e}")
        raise

if __name__ == "__main__":
    app.run(manage_connection())
    app.idle()  # Bot ko continuously run karne aur messages sunne ke liye
