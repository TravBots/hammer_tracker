from time import sleep
import discord
import asyncio
import sys
import os
import threading
import requests

path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print("Appending path:", path)
sys.path.append(path)

from core import Core
from utils.logger import setup_logging

# Add these global events
process_lock = threading.Event()


class TestCore(Core):
    success_values = {
        0: "Database initialized",
        1: "Set admin_role as ADMIN",
        2: "Set user_role as USER",
        3: "Set game_server as https://ts2.x1.europe.travian.com",
        4: "No results found for test",
    }
    success_counter = 0

    async def on_message(self, message):
        # Check if message has embeds before trying to access them
        if message.embeds and message.author == self.user:
            embed_fields = message.embeds[0].fields
            print(
                f"Message received: {embed_fields}; author is self?: {message.author == self.user}"
            )
            if self.success_values[self.success_counter] in embed_fields[0].value:
                print(
                    f"Successfully received {self.success_values[self.success_counter]}"
                )
                self.success_counter += 1
                process_lock.set()

        # Call the parent class's on_message handler
        await super().on_message(message)


async def main():

    @client.event
    async def on_ready():
        print("Bot is ready!")
        process_lock.set()  # Signal that the client is connected

    await client.start(client.token)


def run_discord_client():
    setup_logging()
    asyncio.run(main())


def post_to_webhook(webhook_url: str, message: str):
    data = {
        "content": message,
        "username": "Boink CI/CD",
    }
    result = requests.post(webhook_url, json=data)
    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(f"Not sent with {result.status_code}, response:\n{result.json()}")


def test_command(webhook_url: str, message: str):
    post_to_webhook(webhook_url, message)

    if not process_lock.wait(timeout=30):
        print(f"Failed on command {message} within 30 seconds")
        sys.exit(1)
    else:
        process_lock.clear()
        print(f"Command {message} successful!")


if __name__ == "__main__":
    # Set webhook url from the first argument
    webhook_url = None
    if len(sys.argv) > 1:
        webhook_url = sys.argv[1]
    else:
        print("No webhook URL provided")
        sys.exit(1)

    # Update client initialization to use TestCore
    intents = discord.Intents.all()
    intents.message_content = True
    client = TestCore(intents=intents)

    client_thread = threading.Thread(target=run_discord_client, daemon=True)
    client_thread.start()

    # Wait for client to be ready (with timeout)
    if not process_lock.wait(timeout=30):
        print("Failed to connect to Discord within 30 seconds")
        sys.exit(1)
    else:
        process_lock.clear()
        print("Connected to Discord")

    post_to_webhook(
        webhook_url, "$$$$$$$$$$$$$$$$$$$$$$ Starting tests$$$$$$$$$$$$$$$$$$$$$$"
    )

    test_command(webhook_url, "!boink init")
    test_command(webhook_url, "!boink set admin_role ADMIN")
    test_command(webhook_url, "!boink set user_role USER")
    test_command(
        webhook_url, "!boink set game_server https://ts2.x1.europe.travian.com"
    )
    test_command(webhook_url, "!boink search test")

    post_to_webhook(
        webhook_url, "$$$$$$$$$$$$$$$$$$$$$$ Tests completed $$$$$$$$$$$$$$$$$$$$$$"
    )
    print("All tests completed successfully!")
