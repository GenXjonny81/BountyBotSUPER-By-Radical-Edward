#!/usr/bin/env python3
"""
setup_bountybot.py
Radical Edward–flavored config wizard for BountyBot — your grid trading partner.
"""

import os
import json
from getpass import getpass
import requests
import sys

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

def has_rw_permission(path):
    parent = os.path.dirname(os.path.abspath(path)) or "."
    can_write = os.access(parent, os.W_OK)
    if os.path.exists(path):
        can_write = can_write and os.access(path, os.W_OK)
    can_read = os.access(path, os.R_OK) if os.path.exists(path) else True
    return can_read and can_write

if not has_rw_permission(CONFIG_PATH):
    print(f"\nEd Error! You can't r/w {CONFIG_PATH}. Try: sudo chown $USER {CONFIG_PATH} && chmod u+rw {CONFIG_PATH}")
    sys.exit(2)

import sys
def has_write_permission(path):
    parent = os.path.dirname(os.path.abspath(path)) or "."
    return os.access(parent, os.W_OK)

def api_key_setup_ed():
    print("\n--- API Key Setup! Ed loves secrets! ---")
    dest = ask("Where should Ed hide your super secret key file? (Be sneaky!)", default=os.path.expanduser("~/bountybot.key"))
    if os.path.exists(dest):
        print(f"  Oh! Ed found a key at {dest}. Let’s check if it’s good—and not from the bad guys!")

        with open(dest, "r") as f:
            lines = [line.strip() for line in f.read().strip().splitlines()]
            if len(lines) == 2 and all(len(line) == 32 for line in lines):
                print("  Secrets are safe and sound. Hurray for Ed security!")
                return dest
            else:
                print("  Whoopsy! That key file is incomplete or misformatted. Time to make it shiny and new.")

    def is_valid_key(s):
        return len(s) == 32
    while True:
        try:
            print("\nOkie-dokie! Paste your TradeOgre API key and secret below. Ed promises not to share (or eat them)!")
            api_key = getpass("API Key (Ed can’t see your typing!): ").strip()
            api_secret = getpass("API Secret (ssshhh!): ").strip()
            if not (is_valid_key(api_key) and is_valid_key(api_secret)):
                print("Whoa! Ed says: API keys must be exactly 32 characters. Jack back in and try again, cowboy.")
                continue
            if not has_write_permission(dest):
                print(f"\nEd's ICE triggers: Can't write your API key file at {dest}.\n"
                      f"Try running with correct permissions, or pick a new location.\n"
                      f"Hint: sudo chown $USER '{dest}' && chmod u+rw '{dest}'")
                sys.exit(2)
            with open(dest, "w") as f:
                f.write(api_key + "\n" + api_secret + "\n")
            # Optional: place your verify_api_keys check here
            # if not verify_api_keys(api_key, api_secret):
            #     print("Beep-beep! The matrix says your keys are phony—no bounties, no access! Ed says: paste the real deal, chummer!")
            #     continue
            with open(dest, "w") as f:
                f.write(api_key + "\n" + api_secret + "\n")
            print(f"  Zoom! API key is hidden at {dest}. Like a magic Ed trick!")
            try:
                os.chmod(dest, 0o600)
            except Exception:
                pass
            break
        except KeyboardInterrupt:
            print("\n\nRadical Ed caught your Ctrl+C! Exiting the setup—no secrets stolen. See you in cyberspace, cowboy! 👋")
            sys.exit(0)
    return dest

def verify_api_keys(api_key, api_secret):
    # Example for TradeOgre-like API.
    try:
        # API endpoint for self-verification (adjust to your exchange's docs)
        url = "https://tradeogre.com/api/v1/account/balance"
        headers = {"API-KEY": api_key, "API-SECRET": api_secret}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return True
        else:
            print(f"Key verification :( failed :( OhNo! error code: {response.text}")
            return False
    except Exception as e:
        print(f"Error during key verification: {e}")
        return False


def main():
    ascii_bot = r'''                                  _____
                                 |     |
                                |<= - =>|
                                 |_\=/_|   Let's Go Cowboy! 
                           ____ ___|_|___ ____
                          ()___)BountyBot()___)
                          // /|   Super   |\ \\
                         // / |    MEGA   | \ \\
                        (___) |___________| (___)
                        (___)   (_______)   (___)
                        (___)     (___)     (___)
                        (___)      |_|      (___)
                        (___)  ___/___\___   | |
                         | |  |           |  | |
                         | |  |___________| /___\
                        /___\  |||     ||| //   \\
                       //   \\ |||     ||| \\   //
                       \\   // |||     |||  \\ //
                        \\ // ()__)   (__()
                              ///       \\\
                             ///         \\\
                           _///___     ___\\\_
                          |_______|   |_______|'''

    ascii_art = '''
                 ,  xp  u  _                  _  j- _p  _
      _  `N_  *p `b_ b `L q          _ j _@ jF jF _p" _y^
      "*s_ "*, "h_ 9_ 0_"p k &     ,jFjF @ j"_p"_p" _p"  _*"
    *u_  "*,_ 9u_"q_"b_0_Np9p0 b  jLd 0 0 J"jP j@ _M" _m@" __*
  __  "9m__ "*_ 9u_"u_0_9_9_0JL0 fd Fj'd d p"j* a*"_w@" _w*"  __ 
   "^m,_  "*u_"9u_"q_9W"M"p0Jk0]NF0jNFgL@jP_#"w@_a*"__*^" __w*""
  u__  ""*w__"9u_"*u_N_*C4@N0NNNNN##0ZQRpCpCpF_*"_w*" _a*^"  ___
    ""**u___"^m,_"*s"NCNCNDWNNNNNNNNNNEAZEMEm@Lw^__w*""__aw*^""
   *ua___ ""**w__"*wE@6PN@0N###########NNW0Z*EL*^"_am*"" ____am
       """^**wa_IF^*6Z@pNN##############NBDMEZ**""_gw**^"""
      ^^*r*mwwaj_EEZ@qNBN################NNWp49ZEELaam**r**^
         aaaaaaaaZZZZZ##N#################N#EZZZZLaaaaaas
            _aam**r**NNNN################N#EDM*r*mwwag,
              amr*^ZZWMQ#N###############NNMpEZ5^**ua
               -*"EZ*MN@NNBN###########N@ZNEZ*6E"*r
                 "jw*TbN@NN#NN######NNNBWNZNEP*2""
                   -@j*Cp5AWNNNNNNNNNbA@NNC*CP-
                     "w"g"djF0dNNF#0NF#NC4Ch
                       ` @jFjN@JNF0JL0`L"p"
                          @jFj^0 Ft 0 L`
                           ` # # FJF]r"
                               F F #
                                 F                 
                                 
     '''
    print(ascii_bot)
    print("\n=== Ed's BountyBotSuperMEGA Setup Wizard! ===")
    print("Heehee! BountyBot wants to know all your secrets, just like Ed! Let's get weird and code with style!\n")

    config = {}
    config['bot_ticker'] = ask(
        "Yoo-hoo! Ed wants to know: what is the market pair? Example, BTC-XMR! Ed will read your mind!",
        default="BTC-XMR"
    )
    config['bot_balance'] = ask(
        "How many fake internet monies are you trading? (Like XMRs! Give Ed a number, pleeeease!)",
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
            "How much of your fake internet coins (like XTM or SOL) does Ed get to play with for the sell grid?",
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
        if lower > upper:
            print(
                f"\n⚠️ Ed Error! min_price ({lower}) must be less than or equal to max_price ({upper}). ICE triggered, setup aborted.")
            sys.exit(1)
        grid_count = int(config['grid_count'])
        config['grid_spacing'] = (upper - lower) / (grid_count - 1) if grid_count > 1 else 0
        print(f"\nZing! Ed calculated a grid spacing of {config['grid_spacing']} for your bounties!")
    except Exception as ex:
        config['grid_spacing'] = 0
        print(f"\nOops, Ed couldn’t calculate grid_spacing, set to 0. Please check your config! [{ex}]")

    config['api_key_file'] = api_key_setup_ed()
    if not has_rw_permission(CONFIG_PATH):
        print(
            f"\nEd Error! You can't r/w {CONFIG_PATH}. Try: sudo chown $USER {CONFIG_PATH} && chmod u+rw {CONFIG_PATH}")
        sys.exit(2)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)
    print(ascii_art)
    print(
        f"\nWoohoo! BountyBot is now totally set and super-funky!\nConfig file is waiting at: {CONFIG_PATH}\nEd will stick around for more fun! 🤖🍝")
    print(
        "\n[Ed does a somersault on your screen!]\n"
        "All done! Now Ed says: time to keep going, space cowboy!\n"
        "Open your terminal and run:\n\n"
        "    python Run.py\n\n"
        "and BountyBot will start chasing bounties in cyberspace!\n"
        "Wheeee! Ed will watch you from the net! ^_^"
    )

if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nEd saw your hand on the kill-switch! Setup aborted. The matrix will wait for you, cowboy. Start again by typing python setup_bountybot.py\n")
        sys.exit(0)
