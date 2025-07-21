#!/usr/bin/env python3
"""
run.py – Bootstrapper for the TradeOgre USDC/USDT grid bot.

Usage:
    python run.py         # uses config.json from setup.py
    python run.py --once  # run a single grid cycle, then exit
"""
import argparse
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone


CONFIG_FILE = "config.json"
LOG_FILE    = "grid_bot.log"

def load_config(path):
    if not os.path.isfile(path):
        sys.exit(f"Config {path} not found. Run setup.py first.")
    with open(path) as fp:
        return json.load(fp)

def init_logger():
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

def main():
    parser = argparse.ArgumentParser(description="TradeOgre USDC/USDT Grid Bot")
    parser.add_argument("--once", action="store_true", help="execute one cycle and exit")
    args = parser.parse_args()

    cfg = load_config(CONFIG_FILE)
    init_logger()

    bot = TradeOgre(
        cfg["api_key"],
        cfg["api_secret"],
        cfg["order_amount"],
        cfg["grid_spacing"],
        cfg["min_price"],
        cfg["max_price"],
        cfg["max_active_orders"],
    )

    running = True

    def handle_sigterm(signum, frame):
        nonlocal running
        running = False
        logging.info("[Spike’s Log]Shutdown signal received – Later Cowboy!")

    signal.signal(signal.SIGINT,  handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)

    logging.info("[Spike’s Log]Okay the Bot's up. Don't know for how long. . .")

    while running:
        start = datetime.now(timezone.utc)
        try:
            bot.cycle()           # place/cancel orders, sync balances
        except Exception as exc:
            logging.exception("Cycle error: %s", exc)

        # Check after one cycle
        if args.once:
            break

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        time.sleep(max(60.0 - elapsed, 0.1))

    bot.shutdown()
    logging.info("[Spike’s Log]Okay, we got it shutdown, now what?")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
import requests
import logging

class TradeOgre(object):
    """ Maintains a single session between this machine and TradeOgre.

    Specifying a key/secret pair is optional. If not specified, key and
    secret must be specified at the called method.

    Query responses, as received by :py:mod:`requests`, are retained
    as attribute :py:attr:`response` of this object. It is overwritten
    on each query.
    """

    def __init__(self, key, secret, order_amount, grid_spacing, min_price, max_price, max_active_orders):
        """ Create an object with authentication information. """
        self.key = key
        self.secret = secret
        self.order_amount = order_amount
        self.grid_spacing = grid_spacing
        self.min_price = min_price
        self.max_price = max_price
        self.max_active_orders = max_active_orders
        """ Create an object with authentication information.

        :param key: (optional) key identifier for queries to the API
        :type key: str

        :param secret: (optional) actual private key used to sign messages
        :type secret: str

        :returns: None

        """
        self.key = key
        self.secret = secret
        self.uri = 'https://tradeogre.com/api/v1'
        self.response = None
        return
    def fetch_market_price(self):
        # Example: fetch current price from /api/v1/ticker/USDC-USDT
        resp = requests.get("https://tradeogre.com/api/v1/ticker/USDC-USDT")
        ticker = resp.json()
        return float(ticker["price"])

    def fetch_balance(self):
        # Example: GET your balance via POST /api/v1/account/balance
        # Replace with your signed API call!
        payload = {"method": "balance"}
        headers = {
           "Authorization": f"Token {self.key}:{self.secret}"
        }
        resp = requests.post(
            "https://tradeogre.com/api/v1/account/balance",
            headers=headers,
            data=payload
        )
        return resp.json()

    def fetch_orders(self):
        # Replace with your signed call to /api/v1/orders
        payload = {"market": "USDC-USDT"}
        headers = {
           "Authorization": f"Token {self.key}:{self.secret}"
        }
        resp = requests.post("https://tradeogre.com/api/v1/orders", headers=headers, data=payload)
        return resp.json()  # Returns list of open orders

    def place_buy_order(self, price):
        payload = {
            "market": "USDC-USDT",
            "type": "buy",
            "quantity": str(self.order_amount),
            "price": str(price)
        }
        resp = requests.post("https://tradeogre.com/api/v1/order/buy", data=payload, auth=(self.key, self.secret))
        import logging
        logging.info(f"[Spike] Order placed: {side.upper()} {amount}@{price}. Buy order POST status: {resp.status_code},body: {resp.text!r}")
        try:
            data = resp.json
        except Exception as e:
            logging.error(f"[Spike] Tried to parse that response—guess it wasn’t a noodle recipe. Just noise. Response: {resp}")
            return None

    def place_sell_order(self, price, quantity):
        payload = {
            "market": "USDC-USDT",
            "type": "sell",
            "quantity": str(quantity),
            "price": str(price)
        }
        resp = requests.post("https://tradeogre.com/api/v1/order/sell", data=payload, auth=(self.key, self.secret))
        import logging
        logging.info(f"[Spike] Sell-Order placed: {side.upper()} {amount}@{price}. Let’s see if anyone bites.")
        try:
            data = resp.json()
        except Exception as e:
            logging.error(f"[Spike] Tried to parse that response—guess it wasn’t a noodle recipe. Just noise. Response: {resp}")
            return None

    def cancel_order(self, order_id):
        payload = {"order_id": order_id}

        resp = requests.post("https://tradeogre.com/api/v1/order/cancel", data=payload, auth=(self.key, self.secret))
        import logging
        logging.info(f"Cancel order POST status: {resp.status_code}, body: {resp.text!r}")
        try:
            data = resp.json()
        except Exception as e:
            logging.error(f"Non-JSON response: status={resp.status_code}, body={resp.text!r}")
            return None

    def shutdown(self):
        import logging
        logging.info("Grid bot shutdown cleanly. Console cowboy out.")

    def cycle(self):
        orders = None
        try:
            market = "USDC-USDT"

            ticker = self.ticker(market)
            logging.info(f"Raw ticker data: {ticker}")
            if "price" not in ticker:
                logging.warning("No 'price' in ticker! Full ticker response: %r", ticker)
                logging.info(f"Raw balances: {balances}")
                return  # Or handle error accordingly
            price = float(ticker["price"])

            balances = self.balances()
            usdt = float(balances['balances'].get("USDT", 0))
            usdc = float(balances['balances'].get("USDC", 0))
            logging.info(f"[Spike] Checked the wallet for {asset}. Still scraping by. Balance: {resp.get('available', 'N/A')}")
            logging.debug(f"Orders API raw response: {orders}")
            logging.debug(f"Orders: {orders}")

            orders = self.orders(market)
        # Typically a list of dicts, but always LOG to confirm structure:
            logging.debug(f"Fetched orders: {orders}")

        # ...rest of grid logic here...

            # Cancel any extra/invalid grid orders over limit or out-of-range
            active_buys = [o for o in orders if o["type"] == "buy"]
            active_sells = [o for o in orders if o["type"] == "sell"]

            # Cancel excess buy orders if over max_active_orders
            for order in active_buys[self.max_active_orders:]:
                self.cancel_order(order["id"])
                logging.info(f"Cancelled excess buy order at {order['price']}")

            # Place buy orders on grid (if under max_active_orders)
            grid_prices = []
            p = self.min_price
            while p <= self.max_price and len(grid_prices) < self.max_active_orders:
                grid_prices.append(round(p, 6))
                p += self.grid_spacing

            # Place missing buy orders
            for p in grid_prices:
                # Only place a buy if not already an open buy order at that price
                if not any(float(o["price"]) == p for o in active_buys):
                    if usdt >= self.order_amount * p:
                        result = self.place_buy_order(p)
                        logging.info(f"[Spike] Order placed: {self.order_amount} at {p}")
                    else:
                        logging.info("[Spike] Well, that didn’t go as planned. Might need a bigger ship—or a better crew! Not enough USDT!!!")

            # Place sell order for all USDC balance at sell_price if not already exists
            #if usdc > 1 and not any(float(o["price"]) == self.sell_price for o in active_sells):
                result = self.place_sell_order(self.sell_price, usdc)
                logging.info(f"Placed sell order for {usdc} at {self.sell_price}")

            logging.info("Cycle complete.")
        except Exception as e:
            logging.exception(f"Error in cycle: {e}")

    def load_key(self, path):
        """ Load key and secret from file.
        Expected file format is key and secret on separate lines.

        :param path: path to keyfile
        :type path: str

        :returns: None

        """
        #print(path)#debug

        with open(path, 'r') as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()
        return

    def markets(self):
        """ Retrieve a listing of all markets and basic information
        including current price, volume, high, low, bid and ask.

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        self.response = requests.get(self.uri + '/markets').json()
        return self.response

    def order_book(self, market):
        """ Retrieve the current order book for a market such as 'BTC-XMR'.

        :param market: market such as 'BTC-XMR'
        :type market: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        self.response = requests.get(self.uri + '/orders/' + market).json()
        return self.response

    def ticker(self, market):
        """ Retrieve the ticker for a market such as 'BTC-XMR', volume,
        high, and low are in the last 24 hours, initial price is the
        price from 24 hours ago.

        :param market: market such as 'BTC-XMR'
        :type market: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        self.response = requests.get(self.uri + '/ticker/' + market).json()
        return self.response

    def history(self, market):
        """ Retrieve the history of the last trades on {market} limited to 100
        of the most recent trades. The date is a Unix UTC timestamp.

        :param market: market such as 'BTC-XMR'
        :type market: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        self.response = requests.get(self.uri + '/history/' + market).json()
        return self.response

    def balance(self, currency, key=None, secret=None):
        """ Get the balance of a specific currency for you account. The currency
        field is required, such as 'BTC'. The total balance is returned and the
        available balance is what can be used in orders or withdrawn.

        :param currency: currency such as 'BTC'
        :type currency: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data = {"currency": currency}
        self.response = requests.post(self.uri + '/account/balance', data=data, auth=(key, secret)).json()
        return self.response

    def balances(self, key=None, secret=None):
        """ Retrieve all balances for your account.

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        self.response = requests.get(self.uri + '/account/balances', auth=(key, secret)).json()
        return self.response

    def buy(self, market, qty, price, key=None, secret=None):
        """ Submit a buy order to the order book for a market. The success status
        will be false if there is an error, and error will contain the error message.
        Your available buy and sell balance for the market will be returned if
        successful. If your order is successful but not fully fulfilled, the order
        is placed onto the order book and you will receive a uuid for the order.

        :param market: market such as 'BTC-XMR'
        :type market: str

        :param qty: quantity to buy
        :type qty: str

        :param price: price to buy for
        :type price: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data = {"market": market, "quantity": qty, "price": price}
        self.response = requests.post(self.uri + '/order/buy', data=data, auth=(key, secret)).json()
        return self.response

    def sell(self, market, qty, price, key=None, secret=None):
        """ Submit a sell order to the order book for a market. The success status
        will be false if there is an error, and error will contain the error
        message. Your available buy and sell balance for the market will be returned
        if successful. If your order is successful but not fully fulfilled, the order
        is placed onto the order book and you will receive a uuid for the order.

        :param market: market such as 'BTC-XMR'
        :type market: str

        :param qty: quantity to sell
        :type qty: str

        :param price: price to sell for
        :type price: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data = {"market": market, "quantity": qty, "price": price}
        self.response = requests.post(self.uri + '/order/sell', data=data, auth=(key, secret)).json()
        return self.response

    def order(self, uuid, key=None, secret=None):
        """ Retrieve information about a specific order by the
        uuid of the order. Date is a Unix UTC timestamp.

        :param uuid: ID of order
        :type uuid: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        self.response = requests.get(self.uri + '/account/order/' + uuid, auth=(key, secret)).json()
        return self.response

    def orders(self, market=None, key=None, secret=None):
        """ Retrieve the active orders under your account. The market
        field is optional, and leaving it out will return all orders
        in every market. date is a Unix UTC timestamp.

        :param market: (optional) market to list orders from
        :type market: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        if market is None:
            market = ''

        data = {"market": market}
        self.response = requests.post(self.uri + '/account/orders', data=data, auth=(key, secret)).json()
        return self.response

    def cancel(self, uuid, key=None, secret=None):
        """ Cancel an order on the order book based on the order uuid.
        The uuid parameter can also be set to all and all of your
        orders will be cancelled across all markets.

        :param uuid: ID of order to cancel
        :type uuid: str

        :param key: key identifier
        :type key: str

        :param secret: actual private key
        :type secret: str

        :returns: :py:meth:`requests.Response.json`-deserialised Python object

        """
        if key is None or secret is None:
            key = self.key
            secret = self.secret

        if key is None or secret is None:
            raise Exception('Either key or secret is not set! (Use `load_key()`.')

        data = {"uuid": uuid}
        self.response = requests.post(self.uri + '/order/cancel', data=data, auth=(key, secret)).json()
        return self.response