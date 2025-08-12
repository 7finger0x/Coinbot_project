# CoinBot

CoinBot is an automated crypto token tracker and trading bot.  
It fetches new token data from DexScreener and Pump.fun, applies filters to avoid scams, and can automatically place trades via BonkBot.  
The bot also sends real-time alerts to your Telegram.

---

## Features
- **Data Sources**: DexScreener + Pump.fun
- **Rugcheck Integration**: Flags and blacklists scam tokens/developers
- **Fake Volume Detection**: Pocket Universe + heuristic methods
- **Trading**: Automatic buy/sell using BonkBot API
- **Telegram Alerts**: Real-time notifications for pumps, rugs, and listings
- **Auto-Blacklist**: Blocks known bad developers after repeated rugs
- **Configurable Filters**: Control liquidity thresholds, holder concentration, and more

---

## Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YOURUSERNAME/coinbot.git
cd coinbot