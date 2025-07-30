import sys
import argparse
from colorama import Fore, Style, init as colorama_init
from telegather.scraper import scrape_channel, TelegramScraperError


def prompt_int(prompt_text: str) -> int:
    """
    Prompt the user for an integer value until a valid integer is entered.
    """
    while True:
        try:
            raw = input(Fore.YELLOW + prompt_text + Style.RESET_ALL + " ")
            value = int(raw.strip())
            return value
        except ValueError:
            print(Fore.RED + "✗ Invalid integer. Please try again." + Style.RESET_ALL)


def prompt_str(prompt_text: str) -> str:
    """
    Prompt the user for a non-empty string value.
    """
    while True:
        raw = input(Fore.YELLOW + prompt_text + Style.RESET_ALL + " ")
        if raw.strip():
            return raw.strip()
        print(Fore.RED + "✗ This field cannot be empty. Please try again." + Style.RESET_ALL)


def main():
    # Initialize colorama (so colors work on Windows too)
    colorama_init(autoreset=True)

    parser = argparse.ArgumentParser(
        prog="telegather",
        description="Scrape messages from a public Telegram channel and save to CSV.",
    )
    parser.add_argument(
        "--api-id",
        type=int,
        help="Your Telegram API_ID (integer).",
    )
    parser.add_argument(
        "--api-hash",
        type=str,
        help="Your Telegram API_HASH (string).",
    )
    parser.add_argument(
        "--channel",
        type=str,
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

    # If any of the required values are missing, prompt interactively
    if args.api_id is None:
        args.api_id = prompt_int("Enter your Telegram API_ID (integer):")
    if args.api_hash is None:
        args.api_hash = prompt_str("Enter your Telegram API_HASH (string):")
    if args.channel is None:
        args.channel = prompt_str("Enter target channel username (without t.me/):")

    # If limit is None, ask whether to scrape all or a specific number
    if args.limit is None:
        raw = input(
            Fore.YELLOW
            + "Enter number of messages to scrape (leave blank or enter 0 for ALL):"
            + Style.RESET_ALL
            + " "
        ).strip()
        if raw == "" or raw == "0":
            args.limit = None
        else:
            try:
                args.limit = int(raw)
                if args.limit <= 0:
                    args.limit = None
            except ValueError:
                print(Fore.RED + "✗ Invalid integer. Defaulting to ALL messages." + Style.RESET_ALL)
                args.limit = None

    # If output wasn't provided as flag, ask for it (just to confirm/edit)
    if args.output == "msgs.csv":
        raw = input(
            Fore.YELLOW
            + f"Output CSV file path [{args.output}]:"
            + Style.RESET_ALL
            + " "
        ).strip()
        if raw:
            args.output = raw

    # Echo back the provided options (in cyan)
    print(
        f"{Fore.CYAN}→ Starting scrape: channel='{args.channel}', "
        f"limit={args.limit or 'ALL'}, output='{args.output}'{Style.RESET_ALL}"
    )

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


if __name__ == "__main__":
    main()
