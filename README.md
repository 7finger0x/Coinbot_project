# Coinbot_project
Crypto trading bot

CoinBot Project — Setup & Launch Guide

Prerequisites
	•	Python 3.9+ installed
	•	Telegram Bot token from BotFather
	•	BonkBot API key & secret
	•	API keys for Etherscan, BscScan, Solscan, Pocket Universe, Rugcheck (optional)

1) Clone or download the project
git clone https://your-repo-url.git
cd coinbot_project

2) Install dependencies
pip install -r requirements.txt

3) Configure config.yaml

Edit API keys, filters, blacklists, Telegram chat ID, and BonkBot credentials:
telegram:
  token: "YOUR_TELEGRAM_BOT_TOKEN"
  chat_id: "YOUR_TELEGRAM_CHAT_ID"

bonkbot:
  api_key: "YOUR_BONKBOT_API_KEY"
  api_secret: "YOUR_BONKBOT_API_SECRET"

explorers:
  etherscan:
    enabled: true
    api_key: "YOUR_ETHERSCAN_API_KEY"
    base_url: "https://api.etherscan.io/api"
  # other explorers...

pocket_universe:
  enabled: true
  api_key: "YOUR_POCKET_UNIVERSE_API_KEY"
  base_url: "https://api.pocketuniverse.xyz/v1"

filters:
  min_liquidity: 1000
  max_top10_percent: 60

blacklists:
  coins: []
  developers: []

4) Run the bot
 python bot.py

The bot will:
	•	fetch token data
	•	enrich with on-chain info
	•	detect rugs/pumps/listings
	•	automatically trade selected tokens via BonkBot
	•	send Telegram notifications & respond to Telegram commands

5) Telegram commands
	•	/buy <token_address> <amount> — place buy order
	•	/sell <token_address> <amount> — place sell order
	•	/status — check bot trading status

•	DexScreener & Pump.fun data fetching
	•	On-chain enrichment (Etherscan & Solscan)
	•	Filters, blacklists, Pocket Universe volume checks
	•	Rugcheck.xyz verification + bundled supply blocking
	•	BonkBot trading wrapper
	•	Telegram bot integration with commands and real-time notifications
	•	SQLite storage for tokens and dev stats
	•	Config-driven via config.yaml