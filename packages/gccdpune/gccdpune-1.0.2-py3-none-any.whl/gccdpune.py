#!/usr/bin/env python3
import argparse
import re
import os
from pathlib import Path
from colorama import init, Fore, Style

# Version for setup.py
__version__ = "1.0.2"

# Initialize colorama
init(autoreset=True)

# Custom color palette (approximated with colorama ANSI codes)
PASTEL_BLUE = Fore.CYAN  # Headers, prompts
PASTEL_GREEN = Fore.GREEN  # Success, reveal
PASTEL_CORAL = Fore.YELLOW  # Hints
PASTEL_PURPLE = Fore.MAGENTA  # Venue
BRIGHT_RED = Fore.RED  # Errors

def display_welcome():
    """Display an interactive welcome message."""
    print(PASTEL_BLUE + "=" * 50)
    print(Fore.YELLOW + "Welcome to GCCD Pune 2025!")
    print(PASTEL_GREEN + "Join the cloud community in Pune for an epic event!")
    print(PASTEL_PURPLE + "Try these commands:")
    print(PASTEL_PURPLE + "  - `gccdpune --date` for a hint")
    print(PASTEL_PURPLE + "  - `gccdpune DD-MM-YY` to guess (e.g., 12-06-25)")
    print(PASTEL_PURPLE + "  - `gccdpune --venue` for venue info")
    print(PASTEL_PURPLE + "  - `gccdpune --help` for more details")
    print(PASTEL_BLUE + "=" * 50)

def should_show_welcome():
    """Check if welcome message should be shown."""
    home_dir = Path(os.environ.get("USERPROFILE", Path.home()))
    welcome_flag = home_dir / ".gccdpune_welcome"
    try:
        if not welcome_flag.exists():
            welcome_flag.touch()  # Create flag file
            return True
        return False
    except Exception as e:
        print(f"{BRIGHT_RED}Error handling welcome flag: {e}")
        return True  # Show welcome if file access fails

def validate_date_format(date_str):
    """Validate DD-MM-YY format."""
    pattern = r"^\d{2}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_str))

def main():
    parser = argparse.ArgumentParser(
        description="Google Cloud Community Day Pune 2025 Interactive CLI",
        epilog="Commands: `gccdpune --date` for a hint, `gccdpune DD-MM-YY` to guess the date, `gccdpune --venue` for venue info."
    )
    parser.add_argument("--date", action="store_true", help="Get a hint for the event")
    parser.add_argument("--venue", action="store_true", help="Get venue information")
    parser.add_argument("guess", nargs="?", help="Guess the date in DD-MM-YY format (e.g., 12-06-25)")
    args = parser.parse_args()

    # Show welcome message only on first run
    if should_show_welcome():
        display_welcome()

    correct_date = "12-07-25"
    hints = [
        f"{PASTEL_CORAL}Hint: Clouds part in Pune, day is a dozen!{Style.RESET_ALL}",
        f"{PASTEL_CORAL}Hint: The month is a prime number!{Style.RESET_ALL}",
        f"{PASTEL_GREEN}Final reveal: The date is 12 July 2025!{Style.RESET_ALL}"
    ]

    # Track attempts in a file
    home_dir = Path(os.environ.get("USERPROFILE", Path.home()))
    guess_file = home_dir / ".gccdpune_guesses.txt"
    try:
        with open(guess_file, "r") as f:
            attempts = int(f.read())
    except (FileNotFoundError, ValueError):
        attempts = 0

    if args.date:
        print(hints[0])
        print(f"{PASTEL_BLUE}Guess the date with: `gccdpune DD-MM-YY` (e.g., `gccdpune 12-06-25`)")
    elif args.venue:
        print(f"{PASTEL_PURPLE}Thoda sabar karo")
    elif args.guess:
        if not validate_date_format(args.guess):
            print(f"{BRIGHT_RED}Invalid format! Use DD-MM-YY (e.g., 12-06-25)")
            return
        if args.guess == correct_date:
            print(f"{PASTEL_GREEN}Correct! Google Cloud Community Day Pune 2025 is on 12 July 2025!")
            with open(guess_file, "w") as f:
                f.write("0")  # Reset attempts
        else:
            attempts += 1
            with open(guess_file, "w") as f:
                f.write(str(attempts))
            if attempts == 1:
                print(f"{BRIGHT_RED}Wrong guess! {hints[1]}")
                print(f"{PASTEL_BLUE}Try again with: `gccdpune DD-MM-YY` (e.g., `gccdpune 12-06-25`)")
            else:
                print(hints[2])
                with open(guess_file, "w") as f:
                    f.write("0")  # Reset attempts
    else:
        print(f"{PASTEL_BLUE}Get started with `gccdpune --date`, `gccdpune DD-MM-YY`, or `gccdpune --venue`.")

if __name__ == "__main__":
    main()
