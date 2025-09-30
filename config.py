from decouple import config

BINANCE_API_KEY = config("BINANCE_API_KEY", default=None)
BINANCE_SECRET = config("BINANCE_SECRET", default=None)
NTFY_TOPIC = config("NTFY_TOPIC")

EXCHANGE = config("EXCHANGE", default="binance").lower()