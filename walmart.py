import discord
import webbrowser
import re
import os
from dotenv import load_dotenv

load_dotenv()

USER_TOKEN = os.getenv("USER_TOKEN")
CHANNEL_IDS = {
    int(cid.strip())
    for cid in os.getenv("CHANNEL_IDS", "0").split(",")
    if cid.strip()
}

# Target product titles to watch for
TARGET_TITLES = [
    "Pokémon TCG: Scarlet & Violet",
    "Pokemon Trading Card Games Scarlet Violet",
    "Pokémon Mega Evolution",
    "Pokémon TCG: Mega Evolution— Ascended Heroes Elite Trainer Box",
    "Ascended Heroes",
    "Pokémon TCG: Mega Evolution—Ascended Heroes Mini Tin - 10Ct Display",
    "Pokémon Unova Heavy Hitters Premium Collection",
    "Pokémon TCG: Mega Charizard X ex Ultra Premium Collection",
    "Prismatic Evolutions Elite Trainer Box",
    "Costco - Pokémon",
    "EB Games - Ascended Heroes"
]

client = discord.Client()


def extract_url_from_text(text: str) -> str | None:
    """
    Check text for target titles and extract any link.
    """
    if not text:
        return None

    # Check if the text contains any of the target titles (case-insensitive)
    text_lower = text.lower()
    has_target_title = any(target.lower() in text_lower for target in TARGET_TITLES)
    
    if not has_target_title:
        return None

    # Extract first URL found in the text
    match = re.search(r"https?://[^\s<>\"']+", text)
    if match:
        return match.group(0)

    return None


def extract_walmart_url(embed: discord.Embed) -> str | None:
    """
    Check embed for target Pokémon titles and extract any link.
    """
    if not embed.title:
        return None

    # Check if the embed title contains any of the target titles (case-insensitive)
    title_lower = embed.title.lower()
    has_target_title = any(target.lower() in title_lower for target in TARGET_TITLES)
    
    if not has_target_title:
        return None

    # Primary location: embed.url is the hyperlink attached to the title
    if embed.url:
        return embed.url

    # Fallback: scan description for any URL
    if embed.description:
        match = re.search(
            r"https?://[^\s<>\"']+",
            embed.description,
        )
        if match:
            return match.group(0)

    # Fallback: scan each field value
    for field in embed.fields:
        if field.value:
            match = re.search(
                r"https?://[^\s<>\"']+",
                field.value,
            )
            if match:
                return match.group(0)

    return None


@client.event
async def on_ready():
    print(f"[+] Logged in as {client.user}")
    print(f"[+] Watching for Pokémon products:")
    for title in TARGET_TITLES:
        print(f"    - {title}")
    for cid in CHANNEL_IDS:
        channel = client.get_channel(cid)
        if channel:
            print(f"[+] Watching channel: #{channel.name} ({cid})")
        else:
            print(f"[!] WARNING: Could not find channel with ID {cid}. "
                  "Make sure your account is a member of that server/channel.")


@client.event
async def on_message(message: discord.Message):
    # Only watch the configured channels
    if message.channel.id not in CHANNEL_IDS:
        return

    # First check regular message content (for non-embed messages)
    if message.content:
        url = extract_url_from_text(message.content)
        if url:
            print(f"[!] Pokémon Product Detected in message — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message

    # Then check embeds (for webhook messages)
    for embed in message.embeds:
        url = extract_walmart_url(embed)
        if url:
            print(f"[!] Pokémon Product Detected in embed — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message


if __name__ == "__main__":
    if not USER_TOKEN:
        raise SystemExit("[!] USER_TOKEN is not set. Add it to your .env file.")
    if not CHANNEL_IDS or CHANNEL_IDS == {0}:
        raise SystemExit("[!] CHANNEL_IDS is not set. Add it to your .env file.")
    client.run(USER_TOKEN)
