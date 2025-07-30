import sys
import argparse
from colorama import Fore, Style, init as colorama_init
from telegather.scraper import scrape_channel, TelegramScraperError


def main():
    # Initialize colorama (so colors work on Windows too)
    colorama_init(autoreset=True)

    parser = argparse.ArgumentParser(
        prog="telegram-scraper-cli",
        description="Scrape messages from a public Telegram channel and save to CSV.",
    )
    parser.add_argument(
        "--api-id",
        type=int,
        required=True,
        help="Your Telegram API_ID (integer).",
    )
    parser.add_argument(
        "--api-hash",
        type=str,
        required=True,
        help="Your Telegram API_HASH (string).",
    )
    parser.add_argument(
        "--channel",
        type=str,
        required=True,
        help="Target channel username (without t.me/).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Number of messages to scrape (omit or 0 for all).",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="msgs.csv",
        help="Output CSV file path (default: msgs.csv).",
    )
    args = parser.parse_args()

    # Echo back the provided options (in cyan)
    print(f"{Fore.CYAN}→ Starting scrape: channel='{args.channel}', limit={args.limit or 'ALL'}, output='{args.output}'{Style.RESET_ALL}")

    try:
        count = scrape_channel(
            api_id=args.api_id,
            api_hash=args.api_hash,
            channel=args.channel,
            limit=args.limit,
            output_csv=args.output,
        )
        print(f"{Fore.GREEN}✅ Successfully saved {count} messages to '{args.output}'.{Style.RESET_ALL}")
        sys.exit(0)
    except TelegramScraperError as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # Catch‐all, should be rare
        print(f"{Fore.RED}❌ Unexpected error: {e}{Style.RESET_ALL}", file=sys.stderr)
        sys.exit(1)
