# BountyBotSUPER-By-Radical-Edward
Cowboy Bebop themed Python Grid Bot 
# BountyBotSuper

**Grid trading with real Bebop energy — Spike style logs, Ed-style config wizard.**

---

## 🚀 What is BountyBotSuper?

BountyBotSuper is a Python crypto grid trading bot for [TradeOgre.com](https://tradeogre.com).  
It leverages buy and sell grids to automate market making or spot trading — and logs every move with “notes from Spike” or “Ed chatter” so you know what’s really happening in the engine room.

**Features:**
- Radical Ed–style setup wizard: easy, safe, and fun!
- Double-sided grid: buys **and** sells, always flipping back when orders fill.
- Spike Spiegel–style logging (“Bad signal from the endpoint”, etc).
- Trades any TradeOgre pair (BTC-XMR, XTM-USDT, etc.)
- Robust, recoverable, and (optionally) multiplatform.

---

## 🛠️ Setup & Usage

### 1. Clone the Repo

  git clone https://github.com/GenXjonny81/BountyBotSUPER-By-Radical-Edward.git
  cd BountyBotSuper

### 2. Run the Setup Wizard

In setup_bountybot.py Radical Ed helps you configure your market, grid, API keys, and more:

- **NEVER use real API keys for testing, and never commit `bountybot_config.json` or `.key` files to Github!**

### 3. Start Your Bot

Spike, Ed, and Jet will take it from there—with Bebop-style logs and grid action on every trading pulse.

---

## 🔧 Configuration

`setup_bountybot.py` helps you generate a safe config file.  
**Config example (`bountybot_config.json`):**
{
"bot_ticker": "XTM-USDT",
"bot_balance": 2000,
"grid_count": 10,
"max_price": 0.0075,
"min_price": 0.0060,
"order_amount": 200,
"max_active_orders": 10,
"pulse_secs": 60,
"pulse_echo": 5,
"api_key_file": "/home/you/bountybot.key",
... other grid/wizard params
}
> *Tip: Always keep API files, keys, and configs out of your repo and in your `.gitignore`.*

---

## 🛡️ Security

- **Never push real API keys, secrets, or live configs to Github (use .gitignore!).**
- Ed’s wizard stores them in a local file with permissions locked down.

---

## 👾 Logging Style

- Ed: Setup, config, and trades have energetic, playful commentary.
- Spike: API errors and main bot output get laconic, bluesy log entries.
- Jet: Session updates and final shutdown messages.

---

## 🧑‍💻 Requirements

- Python 3.8 or higher
- [requests](https://pypi.org/project/requests/) (`pip install requests`)
- TradeOgre account & API key

---

## 📃 License

MIT License, see `LICENSE`.  
BountyBotSuper is free, open, and always ready for a jam.

---

## 🎷 See You, Space Cowboy...

Grid the market. Flip a bounty. Dance with the blues.  
*Whenever there's jazz, there’s always a trade to chase.*

---


