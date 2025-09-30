import requests
from binance.client import Client as BinanceClient
from pybit.unified_trading import HTTP
from config import EXCHANGE

def get_top_100_excluding_stables():
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    )
    response = requests.get(url, timeout=10)
    data = response.json()

    stables = {"USDT", "USDC", "BUSD", "DAI", "FDUSD", "TUSD", "USDP", "GUSD"}
    coins = []

    if EXCHANGE == "binance":
        client = BinanceClient()
        exchange_info = client.get_exchange_info()
        binance_symbols = {s["symbol"] for s in exchange_info["symbols"] if s["symbol"].endswith("USDT")}
        for coin in data:
            sym = coin["symbol"].upper() + "USDT"
            if coin["symbol"].upper() not in stables and sym in binance_symbols:
                coins.append({"symbol": sym, "name": coin["name"]})

    elif EXCHANGE == "bybit":
        client = HTTP(testnet=False)
        symbols = client.get_instruments_info(category="spot")["result"]["list"]
        bybit_symbols = {s["symbol"] for s in symbols if s["quoteCoin"] == "USDT"}
        for coin in data:
            sym = coin["symbol"].upper() + "USDT"
            if coin["symbol"].upper() not in stables and sym in bybit_symbols:
                coins.append({"symbol": sym, "name": coin["name"]})

    return coins[:100]

