import discord
import webbrowser
import re
import os
import asyncio
from datetime import datetime
from dotenv import load_dotenv


def log(message):
    """Print message with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} {message}")

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

# Create client with optimized settings for connection stability
client = discord.Client(
    heartbeat_timeout=60.0,  # Increased timeout for heartbeat
    max_messages=100  # Limit message cache to reduce memory
)


def extract_pokemon_center_url(embed: discord.Embed) -> str | None:
    """
    Check embed for 'Queue' keyword in title and extract the pokemoncenter.com link.
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


def extract_product_url(embed: discord.Embed) -> str | None:
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
    log(f"[+] Logged in as {client.user}")
    log(f"[+] Watching for:")
    log(f"    - Pokemon Center Queue notifications")
    log(f"    - Target Pokémon products:")
    for title in TARGET_TITLES:
        log(f"      • {title}")
    for cid in CHANNEL_IDS:
        channel = client.get_channel(cid)
        if channel:
            log(f"[+] Watching channel: #{channel.name} ({cid})")
        else:
            log(f"[!] WARNING: Could not find channel with ID {cid}. "
                  "Make sure your account is a member of that server/channel.")


@client.event
async def on_disconnect():
    log(f"[!] Disconnected from Discord - attempting to reconnect...")


@client.event
async def on_resumed():
    log(f"[+] Successfully resumed connection to Discord")


@client.event
async def on_message(message: discord.Message):
    # Only watch the configured channels
    if message.channel.id not in CHANNEL_IDS:
        return

    # First check regular message content (for non-embed messages with target titles)
    if message.content:
        url = extract_url_from_text(message.content)
        if url:
            log(f"[!] Pokémon Product Detected in message — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message

    # Then check embeds
    for embed in message.embeds:
        # First check for Pokemon Center queue
        url = extract_pokemon_center_url(embed)
        if url:
            log(f"[!] Queue Detected — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message
        
        # Then check for target product titles
        url = extract_product_url(embed)
        if url:
            log(f"[!] Pokémon Product Detected in embed — Opening: {url}")
            webbrowser.open(url)
            return  # open only once per message


async def run_bot():
    """Run the bot with automatic reconnection on failures."""
    max_retries = 5
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            await client.start(USER_TOKEN)
        except (discord.ConnectionClosed, discord.GatewayNotFound, 
                ConnectionResetError, asyncio.TimeoutError) as e:
            log(f"[!] Connection error (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                log(f"[+] Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                log("[!] Max retries reached. Exiting.")
                raise
        except Exception as e:
            log(f"[!] Unexpected error: {e}")
            raise


if __name__ == "__main__":
    if not USER_TOKEN:
        raise SystemExit("[!] USER_TOKEN is not set. Add it to your .env file.")
    if not CHANNEL_IDS or CHANNEL_IDS == {0}:
        raise SystemExit("[!] CHANNEL_IDS is not set. Add it to your .env file.")
    
    # Run with automatic reconnection
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        log("\n[+] Bot stopped by user")
    except Exception as e:
        log(f"[!] Fatal error: {e}")
