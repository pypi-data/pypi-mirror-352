import csv
import asyncio
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    ChannelInvalidError,
    ChannelPrivateError,
    RPCError,
    FloodWaitError,
)
from datetime import datetime
from typing import Optional


class TelegramScraperError(Exception):
    """Base exception for scraper errors."""


async def _collect_messages(
    api_id: int,
    api_hash: str,
    channel: str,
    limit: Optional[int],
) -> list[dict]:
    """
    Connects to Telegram, iterates through messages in `channel`,
    and returns a list of dicts: [{'id': ..., 'date': ..., 'text': ...}, ...].
    """
    client = TelegramClient("telegram_scraper_session", api_id, api_hash)
    try:
        await client.start()
    except SessionPasswordNeededError:
        raise TelegramScraperError("Two‐factor authentication is enabled. Please disable or handle separately.")
    except RPCError as e:
        raise TelegramScraperError(f"Failed to start Telegram client: {e}")

    msgs: list[dict] = []
    try:
        # Telethon uses `limit=None` to fetch all messages
        async for msg in client.iter_messages(channel, limit=limit):
            if msg.message:
                msgs.append({
                    "id": msg.id,
                    "date": msg.date.isoformat(),
                    "text": msg.message.replace("\n", " "),
                })
    except ChannelInvalidError:
        raise TelegramScraperError(f"Channel '{channel}' does not exist.")
    except ChannelPrivateError:
        raise TelegramScraperError(f"Channel '{channel}' is private or you have no access.")
    except FloodWaitError as e:
        raise TelegramScraperError(f"Too many requests: must wait {e.seconds} seconds.")
    except RPCError as e:
        raise TelegramScraperError(f"Error while fetching messages: {e}")
    finally:
        await client.disconnect()

    return msgs


def scrape_channel(
    api_id: int,
    api_hash: str,
    channel: str,
    limit: Optional[int],
    output_csv: str,
) -> int:
    """
    High‐level function to fetch messages and write them to CSV.
    Returns the number of messages saved.
    Raises TelegramScraperError on any failure.
    """
    if limit is not None and limit <= 0:
        raise TelegramScraperError("`limit` must be a positive integer or omitted for all messages.")

    # Validate that api_id is an integer
    if not isinstance(api_id, int):
        raise TelegramScraperError("`api_id` must be an integer.")

    # Kick off the asyncio loop and collect messages
    try:
        msgs = asyncio.get_event_loop().run_until_complete(
            _collect_messages(api_id, api_hash, channel, limit)
        )
    except TelegramScraperError:
        raise
    except Exception as e:
        raise TelegramScraperError(f"Unexpected error: {e}")

    if not msgs:
        # Could be empty if channel has no messages or we had an access issue
        raise TelegramScraperError(f"No messages found in channel '{channel}' or access denied.")

    # Write to CSV (with BOM for Excel compatibility)
    try:
        with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "date", "text"])
            writer.writeheader()
            writer.writerows(msgs)
    except Exception as e:
        raise TelegramScraperError(f"Failed to write CSV '{output_csv}': {e}")

    return len(msgs)
