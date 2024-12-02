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
USER_SESSION = os.getenv("USER_SESSION")

# Load channel mappings from the JSON file
with open("chat_list.json", "r") as json_file:
    CHANNEL_MAPPING = json.load(json_file)

# Initialize the Client with user session
app = Client(
    "my_user_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=USER_SESSION,
)
logger.info("Bot started using Session String")

async def check_channel_access():
    try:
        for mapping in CHANNEL_MAPPING:
            source_channel = int(mapping["source"])
            try:
                channel = await app.get_chat(source_channel)
                logger.info(f"Access to source channel {source_channel}: {channel.title}")
            except Exception as e:
                logger.error(f"Error accessing source channel {source_channel}: {e}")
    except Exception as e:
        logger.error(f"Error in channel access check: {e}")

@app.on_message(filters.channel)
async def forward(client, message):
    try:
        for mapping in CHANNEL_MAPPING:
            source_channel = mapping["source"]
            destinations = mapping["destinations"]

            if message.chat.id == int(source_channel):
                for destination in destinations:
                    try:
                        await client.forward_messages(chat_id=int(destination), from_chat_id=message.chat.id, message_ids=message.id)
                        logger.info(f"Forwarded message ID {message.id} from {source_channel} to {destination}")
                        await asyncio.sleep(5)
                    except Exception as e:
                        logger.error(f"Error forwarding message {message.id} to {destination}: {e}")
                await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in forwarding process: {e}")

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

if __name__ == "__main__":
    app.run(manage_connection())
    asyncio.get_event_loop().run_forever()  # Keep the bot running and listening for messages
