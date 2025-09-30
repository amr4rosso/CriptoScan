import pandas as pd
from binance.client import Client as BinanceClient
from pybit.unified_trading import HTTP
from config import EXCHANGE


def fetch_ohlcv(symbol, interval="1d", limit=300):
    if EXCHANGE == "binance":
        client = BinanceClient()
        klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(
            klines,
            columns=[
                "timestamp", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ]
        )
        df["close"] = pd.to_numeric(df["close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df

    elif EXCHANGE == "bybit":
        client = HTTP(testnet=False)
        # Bybit поддерживает интервалы: "1", "3", "5", "15", "30", "60", "120", "240", "360", "720", "D", "W", "M"
        interval_map = {"1d": "D", "1h": "60", "4h": "240"}
        bybit_interval = interval_map.get(interval, "D")

        resp = client.get_kline(
            category="spot",
            symbol=symbol.replace("USDT", "/USDT"),
            interval=bybit_interval,
            limit=limit,
        )

        df = pd.DataFrame(resp["result"]["list"], columns=[
            "timestamp", "open", "high", "low", "close", "volume", "turnover"
        ])
        df["close"] = pd.to_numeric(df["close"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
        df.set_index("timestamp", inplace=True)
        return df

    else:
        raise ValueError(f"Неизвестная биржа: {EXCHANGE}")
