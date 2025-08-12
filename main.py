import asyncio
import logging
import threading
import time
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from coinbot.config import load_config, save_config
from coinbot.enrichment import fetch_onchain_data_async
from coinbot.trading import BonkBotAPI
from coinbot.telegram_bot import TelegramBot
from coinbot.database import Base, Coin, DeveloperStats
from coinbot.filters import (
    token_passes_filters,
    process_token_with_rugcheck
)
from coinbot.fetchers import fetch_dexscreener_data, fetch_pumpfun_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("coinbot")

cfg = load_config()

engine = create_engine("sqlite:///coins.db")
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)

trading_api = BonkBotAPI(cfg["bonkbot"]["api_key"], cfg["bonkbot"]["api_secret"])
telegram_bot = TelegramBot(cfg["telegram"]["token"], cfg["telegram"]["chat_id"], trading_api)

async def process_token(session, token):
    address = token["address"]

    if not process_token_with_rugcheck(cfg, token):
        save_config(cfg)
        return

    enrichment = await fetch_onchain_data_async(cfg, address, token.get("chain", "ethereum"))

    if not token_passes_filters(token, enrichment):
        return

    coin = session.query(Coin).filter_by(address=address).first()
    if not coin:
        coin = Coin(
            name=token.get("name"),
            symbol=token.get("symbol"),
            address=address,
            developer=token.get("developer"),
        )
        session.add(coin)
        logger.info(f"New token found: {coin.symbol} ({coin.address})")

    coin.total_supply = enrichment["total_supply"]
    coin.holder_count = enrichment["holder_count"]
    coin.top10_holder_percent = enrichment["top10_holder_percent"]
    coin.liquidity_usd = enrichment["liquidity_usd"]

    if (
        (enrichment["top10_holder_percent"] > cfg["filters"]["max_top10_percent"]
         or enrichment["liquidity_usd"] < cfg["filters"]["min_liquidity"]
         or token.get("price_change_1h", 0) < -80)
        and not coin.rug_detected
    ):
        coin.rug_detected = True
        logger.warning(f"Rug detected: {coin.symbol}")
        telegram_bot.send_message(f"🚨 Rug detected: {coin.symbol} ({coin.address})")

        dev = coin.developer
        if dev:
            dev_stat = session.query(DeveloperStats).filter_by(developer=dev).first()
            if not dev_stat:
                dev_stat = DeveloperStats(developer=dev, rugs_count=1, last_rug=datetime.utcnow())
                session.add(dev_stat)
            else:
                dev_stat.rugs_count += 1
                dev_stat.last_rug = datetime.utcnow()
            session.commit()

            if cfg["auto_blacklist"]["enabled"] and dev_stat.rugs_count >= cfg["auto_blacklist"]["rug_threshold"]:
                if dev not in cfg["blacklists"]["developers"]:
                    cfg["blacklists"]["developers"].append(dev)
                    save_config(cfg)
                    telegram_bot.send_message(f"⚠️ Auto-blacklisted developer: {dev}")

    if token.get("price_change_5m", 0) > 50 and not coin.pump_detected:
        coin.pump_detected = True
        logger.info(f"Pump detected: {coin.symbol}")
        telegram_bot.send_message(f"🚀 Pump detected: {coin.symbol} ({coin.address})")

        if trading_api.buy(coin.address, "0.1"):
            telegram_bot.send_message(f"🛒 Bought {coin.symbol} due to pump")

    if "Binance" in token.get("exchanges", []) and not coin.tier1_listed:
        coin.tier1_listed = True
        logger.info(f"Tier-1 listing detected: {coin.symbol}")
        telegram_bot.send_message(f"⭐ Tier-1 Listing: {coin.symbol} on Binance")

    if token.get("cex_listing") and not coin.cex_listed:
        coin.cex_listed = True
        logger.info(f"CEX listing detected: {coin.symbol}")
        telegram_bot.send_message(f"🏦 CEX Listing detected: {coin.symbol}")

    session.commit()

async def main_loop():
    session = Session()
    try:
        logger.info("Fetching DexScreener data...")
        dex_tokens = fetch_dexscreener_data()
        logger.info(f"Got {len(dex_tokens)} tokens from DexScreener")

        logger.info("Fetching Pump.fun data...")
        pump_tokens = fetch_pumpfun_data()
        logger.info(f"Got {len(pump_tokens)} tokens from Pump.fun")

        all_tokens = dex_tokens + pump_tokens

        for token in all_tokens:
            await process_token(session, token)

    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    threading.Thread(target=telegram_bot.start, args=(cfg["telegram"]["token"],), daemon=True).start()

    while True:
        asyncio.run(main_loop())
        time.sleep(cfg.get("poll_interval_seconds", 300))