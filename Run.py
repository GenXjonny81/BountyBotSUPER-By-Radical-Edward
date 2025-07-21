#!/usr/bin/env python3

# See you, space cowboy...

import time
import json
import tradeogre
from tradeogre import TradeOgre
from funcs import *

# ----[ CONFIG ]-----------------------------------------------
with open("bountybot_config.json") as f:
    CONFIG = json.load(f)

# Load API creds
with open(CONFIG['api_key_file']) as f:
    key = f.readline().strip()
    secret = f.readline().strip()

# Create TradeOgre instance using only config args
trade_ogre = tradeogre.TradeOgre(
    key,
    secret,
    CONFIG["order_amount"],
    CONFIG["grid_spacing"],
    CONFIG["min_price"],
    CONFIG["max_price"],
    CONFIG["max_active_orders"]
)
# ------------------------------------------------------------

def log(msg):
    """Print, Bebop style."""
    print(f"{get_time()} -- {msg}")

def sleepy(secs=1):
    """Jazz break."""
    time.sleep(secs)

ticker = trade_ogre.ticker(CONFIG['bot_ticker'])
if not ticker or 'ask' not in ticker:
    print(f"~*~~*~ ED PANIC!! {CONFIG['bot_ticker']} ticker lost in cyberspace. No 'ask' found! Look: {ticker} -- Bouncy, bounce, fix the connection, puhpuhpuhlease! ~*~~*~")
    exit(1)
sleepy()
btc_bal = trade_ogre.balance(ticker_base_currency(CONFIG['bot_ticker']))['available']
sleepy()
pair_bal = trade_ogre.balance(ticker_pair_currency(CONFIG['bot_ticker']))['available']
def get_balance_safe(asset):
    try:
        resp = trade_ogre.balance(asset)
        if not isinstance(resp, dict) or 'available' not in resp:
            print(f"(>^_^)> [ED-ALERT] Balance vanish! Asset={asset}. API mumbled: {resp} ~ Chasing it through cyberspace now!")
            return 0.0
        return float(resp['available'] or 0)
    except Exception as ex:
        print(f"ED KA-BOOM! Trouble grabbing balance for {asset}! Exception says: {ex} ... Ed rolls across keyboard dramatically!")
        return 0.0
def place_order_safe(side, ticker, amount, price):
    try:
        if side == 'buy':
            resp = trade_ogre.buy(ticker, amount, price)
        else:
            resp = trade_ogre.sell(ticker, amount, price)
        if not isinstance(resp, dict):
            print(f"(=^.^=) ED SQUAWK! {side.upper()} order glitched—got a weird response: {resp} :O")
            return None
        if not resp.get("success", True):
            print(f"ED RASPBERRY! {side.upper()} order REJECTED at {price}! API says: {resp.get('error', resp)} Whyyyyy?! >_<")
            return None
        if "uuid" not in resp:
            print(f"ED FACEPLANT! {side.upper()} order at {price} has no uuid! Mysterious API: {resp} ... Ed grabs skateboard and chases it.")
            return None
        return resp
    except Exception as exc:
        print(f"(x_X) ED EXPLODE! {side.upper()} order at {price} blew up with: {exc} ... Send help! WHEEE!")
        return None


def bountiful_log(cfg, btc_bal, pair_bal, bot_trade_size):
    """Startup log, Bebop chatter."""
    print(f"-- [==BountyBotSUPER==trading==>: {cfg['bot_ticker']}] --")
    print(f"-- Gridding {cfg['grid_count']} trades @ {bot_trade_size} creds each. --")
    print(f"-- Wallet check: {ticker_base_currency(cfg['bot_ticker'])}: {btc_bal} | {ticker_pair_currency(cfg['bot_ticker'])}: {pair_bal} --\n")

if __name__ == '__main__':
    try:
        ticker = trade_ogre.ticker(CONFIG['bot_ticker'])
        if not isinstance(ticker, dict) or 'ask' not in ticker:
            raise ValueError(f"Bad ticker data: {ticker}")
    except Exception as exc:
        print(f"[Ed WARN] Cannot fetch market ticker for {CONFIG['bot_ticker']}: {exc}")
        exit(1)
    # --- Init & grid setup ---
    lower = float(ticker['ask']) + CONFIG['buffer']
    print("DEBUG: Ticker response:", ticker)
    bot_trade_size = CONFIG['order_amount']
    grid_count = CONFIG['grid_count']
    upper = CONFIG['max_price']
    grid_levels = generate_grid(lower, upper, grid_count)
    gridstep = grid_levels[1] - grid_levels[0]
    current_price = float(ticker['ask'])
    bountiful_log(CONFIG, btc_bal, pair_bal, bot_trade_size)
    # Split grid into buy (below) and sell (at/above) bands
    buy_prices = [p for p in grid_levels if p < current_price]
    sell_prices = [p for p in grid_levels if p >= current_price]

    orders = []
    asset_base = ticker_base_currency(CONFIG['bot_ticker'])   # XTM
    asset_quote = ticker_pair_currency(CONFIG['bot_ticker'])  # USDT

    # --- Place buy grid orders below current price ---
    for price in buy_prices:
        bal_usdt = float(trade_ogre.balance(asset_quote).get('available', 0) or 0)
        if bot_trade_size * price < 1:
            print(f"Skipping BUY @{price}, size below minimum!")
            continue
        if bot_trade_size * price > bal_usdt:
            print(f"Not enough USDT for BUY {bot_trade_size} {asset_base} @ {price}")
            continue
        resp = trade_ogre.buy(CONFIG['bot_ticker'], bot_trade_size, price)
        if 'uuid' in resp:
            orders.append({'uuid': resp['uuid'], 'type': 'buy', 'price': price})
        sleepy(0.2)

    # --- Place sell grid orders at/above current price ---
    for price in sell_prices:
        bal_xtm = get_balance_safe(asset_base)
        if bot_trade_size > bal_xtm:
            print(f"Not enough {asset_base} for SELL {bot_trade_size} @ {price}")
            continue
        resp = trade_ogre.sell(CONFIG['bot_ticker'], bot_trade_size, price)
        if 'uuid' in resp:
            orders.append({'uuid': resp['uuid'], 'type': 'sell', 'price': price})
        sleepy(0.2)

    print("Jet: Orders placed. Let the cosmic jazz commence.")
    trades_filled = 0
    pulse = 0
    error_count = 0

    # --- Main event loop ---
    pulse = 0
    trades_filled = 0
    error_count = 0

    try:
        while True:
            try:
                sleepy(CONFIG['pulse_secs'])
                pulse += 1

                open_uuids = [o['uuid'] for o in trade_ogre.orders(CONFIG['bot_ticker'])]

                for order in orders:
                    if order['uuid'] not in open_uuids:
                        print(f"Ed: Order at {order['price']} filled, time to FLIP! 🤩")
                        # Flip logic
                        if order['type'] == 'sell':
                            order['type'] = 'buy'
                            order['price'] -= gridstep
                            resp = trade_ogre.buy(CONFIG['bot_ticker'], bot_trade_size, order['price'])
                        else:
                            order['type'] = 'sell'
                            order['price'] += gridstep
                            resp = trade_ogre.sell(CONFIG['bot_ticker'], bot_trade_size, order['price'])
                        order['uuid'] = resp['uuid']
                        print(f"Ed: Now {order['type']} at {order['price']}... WHEEE!")
                        trades_filled += 1

                if pulse == CONFIG['pulse_echo']:
                    log(f"~o~ ED PULSE CHECK ~o~ Errors: {error_count}, Bounties: {trades_filled}")
                    pulse = 0

            except Exception as loop_ex:
                print(f"[Ed LOOP EXCEPTION!!!] {loop_ex}")
                error_count += 1

    except KeyboardInterrupt:
        print("\n[Jack-out] Session ended by user. See you, space cowboy!")
    except Exception as boss_ex:
        print(f"[Ed CRIT] FATAL UNHANDLED: {boss_ex}")

