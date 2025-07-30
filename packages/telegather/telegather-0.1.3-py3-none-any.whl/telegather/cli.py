import sys
import os
import argparse
from colorama import Fore, Back, Style, init as colorama_init
from telegather.scraper import scrape_channel, TelegramScraperError


def clear_screen():
    """Clears the terminal screen (works on Windows/Linux/macOS)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    """Print a big, colored banner at the top of the screen."""
    width = 42
    top_bot = "═" * width
    empty_line = " " * width

    print(Fore.MAGENTA + Style.BRIGHT + f"╔{top_bot}╗")
    print(f"║{empty_line}║")
    title = "   T E L E G A T H E R   v0.1.3  "
    title = title.center(width)
    print(f"║{title}║")
    subtitle = " A Telegram → CSV Scraper Tool "
    subtitle = subtitle.center(width)
    print(f"║{subtitle}║")
    print(f"║{empty_line}║")
    print(f"╚{top_bot}╝" + Style.RESET_ALL)
    print()  # blank line underneath


def prompt_int(prompt_text: str) -> int:
    """Prompt the user repeatedly until they enter a valid integer."""
    while True:
        raw = input(Fore.YELLOW + prompt_text + Style.RESET_ALL + " ").strip()
        try:
            return int(raw)
        except ValueError:
            print(Fore.RED + "✗ Invalid integer. Please try again." + Style.RESET_ALL)


def prompt_str(prompt_text: str) -> str:
    """Prompt the user repeatedly until they enter a non-empty string."""
    while True:
        raw = input(Fore.YELLOW + prompt_text + Style.RESET_ALL + " ").strip()
        if raw:
            return raw
        print(Fore.RED + "✗ This field cannot be empty. Please try again." + Style.RESET_ALL)


def main():
    # Initialize colorama (so colors work on Windows too)
    colorama_init(autoreset=True)

    # First, clear the screen and print our banner
    clear_screen()
    print_banner()

    # Set up argparse as before, but with no required=True flags
    parser = argparse.ArgumentParser(
        prog="telegather",
        description="Scrape messages from a public Telegram channel and save to CSV.",
        add_help=False  # we’ll handle -h/--help ourselves below
    )
    parser.add_argument("--api-id", type=int, help="Your Telegram API_ID (integer).")
    parser.add_argument("--api-hash", type=str, help="Your Telegram API_HASH (string).")
    parser.add_argument("--channel", type=str, help="Target channel username (without t.me/).")
    parser.add_argument("--limit", type=int, default=None, help="Number of messages to scrape (0 or blank = ALL).")
    parser.add_argument("--output", type=str, default="msgs.csv", help="Output CSV file path (default: msgs.csv).")
    parser.add_argument("-h", "--help", action="store_true", help="Show this help message and exit.")

    args = parser.parse_args()

    # If user asked for help, show standard help and exit
    if args.help:
        parser.print_help()
        sys.exit(0)

    # --------------------------------------------------------------------------------
    # 1) Prompt for API_ID if not provided as a flag
    if args.api_id is None:
        print(Fore.CYAN + "→ [Step 1/4] Enter your Telegram API_ID" + Style.RESET_ALL)
        args.api_id = prompt_int("   API_ID (integer):")

    # 2) Prompt for API_HASH if not provided
    if args.api_hash is None:
        print(Fore.CYAN + "\n→ [Step 2/4] Enter your Telegram API_HASH" + Style.RESET_ALL)
        args.api-hash = prompt_str("   API_HASH (string):")

    # 3) Prompt for CHANNEL if not provided
    if args.channel is None:
        print(Fore.CYAN + "\n→ [Step 3/4] Enter the target channel username" + Style.RESET_ALL)
        args.channel = prompt_str("   Channel username (without t.me/):")

    # 4) Prompt for LIMIT (allow blank or 0 → ALL)
    if args.limit is None:
        print(Fore.CYAN + "\n→ [Step 4/4] How many messages to scrape?" + Style.RESET_ALL)
        raw = input(Fore.YELLOW + "   Enter a number (blank or 0 = ALL):" + Style.RESET_ALL + " ").strip()
        if raw == "" or raw == "0":
            args.limit = None
        else:
            try:
                val = int(raw)
                args.limit = val if val > 0 else None
            except ValueError:
                print(Fore.RED + "✗ Invalid integer. Defaulting to ALL." + Style.RESET_ALL)
                args.limit = None

    # If the user didn’t explicitly pass --output (so it’s still “msgs.csv”), confirm/edit
    print()
    raw_out = input(
        Fore.YELLOW
        + f"Output CSV file path [{args.output}]:"
        + Style.RESET_ALL
        + " "
    ).strip()
    if raw_out:
        args.output = raw_out

    # --------------------------------------------------------------------------------
    # Finally, show a summary “You entered…” before starting
    print()
    print(Fore.MAGENTA + Style.BRIGHT + "───────────────────────────────────────────────" + Style.RESET_ALL)
    print(
        f"{Fore.CYAN}→ About to scrape from channel: {Fore.YELLOW}{args.channel}\n"
        f"{Fore.CYAN}   API_ID:        {Fore.YELLOW}{args.api_id}\n"
        f"{Fore.CYAN}   API_HASH:      {Fore.YELLOW}{args.api_hash}\n"
        f"{Fore.CYAN}   Limit:         {Fore.YELLOW}{(args.limit or 'ALL')}\n"
        f"{Fore.CYAN}   Output CSV:    {Fore.YELLOW}{args.output}{Style.RESET_ALL}"
    )
    print(Fore.MAGENTA + Style.BRIGHT + "───────────────────────────────────────────────" + Style.RESET_ALL)
    print()

    # Begin the actual scraping
    try:
        count = scrape_channel(
            api_id=args.api_id,
            api_hash=args.api_hash,
            channel=args.channel,
            limit=args.limit,
            output_csv=args.output,
        )
        print(Fore.GREEN + f"✅ Successfully saved {count} messages to '{args.output}'.")
        sys.exit(0)

    except TelegramScraperError as e:
        print(Fore.RED + f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(Fore.RED + f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
