import discord
import webbrowser
import re
import os
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv("USER_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "0"))

client = discord.Client()


def extract_pokemon_center_url(embed: discord.Embed) -> str | None:
    """
    Check embed for 'Queue' = keyword title and extract the pokemoncenter.com link.
    """
    # Must have "Queue" somewhere in the title (case-insensitive)
    if not embed.title or "queue" not in embed.title.lower():
        return None

    # Primary location: embed.url is the hyperlink attached to the title
    if embed.url and "pokemoncenter.com" in embed.url:
        return embed.url

    # Fallback: scan description for a pokemoncenter.com URL
    if embed.description:
        match = re.search(
            r"https?://[^\s<>\"']*pokemoncenter\.com[^\s<>\"']*",
            embed.description,
        )
        if match:
            return match.group(0)

    # Fallback: scan each field value
    for field in embed.fields:
        if field.value:
            match = re.search(
                r"https?://[^\s<>\"']*pokemoncenter\.com[^\s<>\"']*",
                field.value,
            )
            if match:
                return match.group(0)

    return None


@client.event
async def on_ready():
    print(f"[+] Logged in as {client.user}")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        print(f"[+] Watching channel: #{channel.name} ({CHANNEL_ID})")
    else:
        print(f"[!] WARNING: Could not find channel with ID {CHANNEL_ID}. "
              "Make sure your account is a member of that server/channel.")


@client.event
async def on_message(message: discord.Message):
    # Only watch the configured channel
    if message.channel.id != CHANNEL_ID:
        return

    for embed in message.embeds:
        url = extract_pokemon_center_url(embed)
        if url:
            print(f"[!] Queue Detected — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message


if __name__ == "__main__":
    if not USER_TOKEN:
        raise SystemExit("[!] USER_TOKEN is not set. Add it to your .env file.")
    if CHANNEL_ID == 0:
        raise SystemExit("[!] CHANNEL_ID is not set. Add it to your .env file.")
    client.run(USER_TOKEN)
