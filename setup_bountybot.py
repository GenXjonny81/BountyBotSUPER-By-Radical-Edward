#!/usr/bin/env python3
"""
setup_bountybot.py
Radical Edward–flavored config wizard for BountyBot — your grid trading partner.
"""

import os
import json
from getpass import getpass

CONFIG_PATH = "bountybot_config.json"

def ask(prompt, default=None, is_float=False, is_int=False, required=True):
    while True:
        d = f" [{default}]" if default is not None else ""
        val = input(f"{prompt}{d}: ").strip()
        if not val and default is not None:
            val = default
        if not val and not required:
            return ""
        try:
            if is_float:
                return float(val)
            if is_int:
                return int(val)
            return val
        except ValueError:
            print("  Heehee! That's not a number, try again!")

def api_key_setup_ed():
    print("\n--- API Key Setup! Ed loves secrets! ---")
    dest = ask("Where should Ed hide your super secret key file? (Be sneaky!)", default=os.path.expanduser("~/bountybot.key"))
    if os.path.exists(dest):
        print(f"  Oh! Ed found a key at {dest}. Let’s check if it’s good—and not from the bad guys!")
        with open(dest, "r") as f:
            lines = f.read().strip().splitlines()
            if len(lines) >= 2 and all(lines):
                print("  Secrets are safe and sound. Hurray for Ed security!")
                return dest
            else:
                print("  Whoopsy! That key file is incomplete. Time to make it shiny and new.")
    print("\nOkie-dokie! Paste your TradeOgre API key and secret below. Ed promises not to share (or eat them)!")
    api_key = getpass("API Key (Ed can’t see your typing!): ")
    api_secret = getpass("API Secret (ssshhh!): ")
    with open(dest, "w") as f:
        f.write(api_key.strip() + "\n" + api_secret.strip() + "\n")
    print(f"  Zoom! API key is hidden at {dest}. Like magic Ed trick!")
    try:
        os.chmod(dest, 0o600)
    except Exception:
        pass
    return dest

def main():
    print("\n=== Ed's Super BountyBot Setup Wizard! ===")
    print("Heehee! BountyBot wants to know all your secrets, just like Ed! Let's get weird and code with style!\n")

    config = {}
    config['bot_ticker'] = ask(
        "Yoo-hoo! Ed wants to know: what is the market pair? Example, BTC-XMR! Ed will read your mind!",
        default="BTC-XMR"
    )
    config['bot_balance'] = ask(
        "How many shinies are you trading? (Like XMRs! Give Ed a number, pleeeease!)",
        is_float=True,
        default="1"
    )
    print("Yoohoo! Ed wants to know how your grid bot will jam through the stars!")
    print(" Pick a style for the cosmic grid:")
    print("  1. Only place buy grids below current price (catch falling stars!)")
    print("  2. Only place sell grids above current price (launch them to the moon!)")
    print("  3. Place BOTH buy and sell grids! (Wheeee! All directions! 🤖🌀)")
    grid_mode = ask(
        "Which grid mode, space explorer? (1, 2, or 3)",
        default="3",
        is_int=True
    )
    config['grid_mode'] = grid_mode

    if grid_mode in [1, 3]:
        config['usdt_allocation'] = ask(
            "How many shiny USDTs for Ed to use on the buy grid? (e.g. 100, or ALL for wild Ed moves!)",
            is_float=True,
            default="50"
        )
    if grid_mode in [2, 3]:
        config['base_allocation'] = ask(
            "How much of your base asset (like XTM or SOL) does Ed get to play with for the sell grid?",
            is_float=True,
            default="10"
        )
    config['grid_count'] = ask(
        "How many pieces do we cut it into? (Grid count! Ed loves grids almost as much as tofu!)",
        default="6",
        is_int=True
    )
    config['max_active_orders'] = ask(
        "Wow! How many orders do you want zooming around at once? (Max active orders—Ed loves lots and lots!)",
        is_int=True,
        default=str(config.get('grid_count', "6"))
    )
    config['max_price'] = ask(
        "High, high, higher! What’s the tippy-top price for this bounty chase?",
        is_float=True,
        default="0.1"
    )
    config['min_price'] = ask(
        "Low, low, lowest! What’s the minimum price for your daring bounties? (Ed loves crawling in the basement!)",
        is_float=True,
        default="0.0069"
    )
    config['buffer'] = ask(
        "Just a teensy-weensy gap between trades—buffer time! How much buffer is enough weird?",
        is_float=True,
        default="0.000005"
    )
    config['pulse_secs'] = ask(
        "How fast should Ed pulse like a hyperactive puppy? (How many seconds between pulses?)",
        is_int=True,
        default="60"
    )

    config['pulse_echo'] = ask(
        "After how many pulses should Ed beep-boop you with news? Count them! (Pulses until update print!)",
        is_int=True,
        default="12"
    )

    # Calculate order amount
    try:
        config['order_amount'] = float(config['bot_balance']) / int(config['grid_count'])
    except Exception:
        config['order_amount'] = float(config['bot_balance'])
    print(f"\nTadaaa! Ed calculated: Each order uses {config['order_amount']} of your precious asset. Radical math, yes?!")

    # Calculate grid spacing
    try:
        lower = float(config['min_price'])  # For a basic grid; you can later improve to use actual min price if you fetch it
        upper = float(config['max_price'])
        grid_count = int(config['grid_count'])
        config['grid_spacing'] = (upper - lower) / (grid_count - 1) if grid_count > 1 else 0
        print(f"\nZing! Ed calculated a grid spacing of {config['grid_spacing']} for your bounties!")
    except Exception as ex:
        config['grid_spacing'] = 0
        print(f"\nOops, Ed couldn’t calculate grid_spacing, set to 0. Please check your config! [{ex}]")

    config['api_key_file'] = api_key_setup_ed()

    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

    print(
        f"\nWoohoo! BountyBot is now totally set and super-funky!\nConfig file is waiting at: {CONFIG_PATH}\nEd will stick around for more fun! 🤖🍝")
    print(
        "\n[Ed does a somersault on your screen!]\n"
        "All done! Now Ed says: time to keep going, space cowboy!\n"
        "Open your terminal and run:\n\n"
        "    python run.py\n\n"
        "and BountyBot will start chasing bounties in cyberspace!\n"
        "Wheeee! Ed will watch you from the net! ^_^"
    )

if __name__ == "__main__":
    main()
