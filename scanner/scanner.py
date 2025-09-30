import requests
import logging
from .fetch_data import fetch_ohlcv
from .indicator import calculate_signals
from .get_top_coins import get_top_100_excluding_stables
from config import NTFY_TOPIC

logger = logging.getLogger(__name__)

def format_price(price: float) -> str:
    if price >= 100:
        return f"{price:.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    elif price >= 0.01:
        return f"{price:.6f}"
    else:
        return f"{price:.8f}"


def scan_and_send(mode: str = "One per Trend") -> None:
    """Основной сканер: перебирает топовые монеты и отправляет сигналы."""
    coins = get_top_100_excluding_stables()
    signals = []

    logger.info(f"Запускаем сканирование в режиме {mode}, монет найдено: {len(coins)}")

    for coin in coins:
        try:
            # Получаем данные OHLCV
            df = fetch_ohlcv(coin["symbol"])
            if df is None or len(df) < 200:
                logger.warning(f"Пропускаем {coin['symbol']} — мало данных")
                continue

            # Считаем сигналы
            df = calculate_signals(df, mode=mode)
            last_row = df.iloc[-1]

            # Проверяем сигналы
            if last_row["long_signal"]:
                message = (
                    f"🟢 LONG сигнал\n"
                    f"Монета: {coin['symbol']} ({coin['name']})\n"
                    f"💵 Цена: {format_price(last_row['close'])} USDT"
                )
                signals.append(message)
                send_ntfy(message, coin["symbol"])
                logger.info(f"LONG сигнал для {coin['symbol']}")

            elif last_row["short_signal"]:
                message = (
                    f"🔴 SHORT сигнал\n"
                    f"Монета: {coin['symbol']} ({coin['name']})\n"
                    f"💵 Цена: {format_price(last_row['close'])} USDT"
                )
                signals.append(message)
                send_ntfy(message, coin["symbol"])
                logger.info(f"SHORT сигнал для {coin['symbol']}")

        except Exception as e:
            logger.error(f"Ошибка для {coin['symbol']}: {e}", exc_info=True)

    # Итоговое сообщение
    if signals:
        summary = "📢 Сигналы сегодня:\n\n" + "\n\n".join(signals)
    else:
        summary = "✅ Сегодня сигналов нет"

    send_ntfy(summary)
    logger.info("Сканирование завершено")


def send_ntfy(message: str, symbol: str | None = None) -> None:
    """Отправка уведомления в ntfy.sh"""
    url = NTFY_TOPIC
    headers = {
        "Title": "Crypto Signal",
        "Content-Type": "text/plain; charset=utf-8",
    }

    # В заголовках — только ASCII (никаких эмодзи!)
    if symbol:
        tv_url = f"https://www.tradingview.com/chart/?symbol=BINANCE:{symbol}"
        headers["Actions"] = f"view, Open TradingView, {tv_url}"

    try:
        resp = requests.post(url, data=message, headers=headers, timeout=10)
        resp.raise_for_status()
        logger.info(f"ntfy: отправлено сообщение для {symbol or 'SUMMARY'}")
    except requests.RequestException as e:
        body = getattr(e.response, "text", None)
        logger.error(f"Ошибка отправки ntfy: {e}. Ответ: {body!r}")



