from phemex_client import PhemexClient
from candle import CandleData
from logger import get_logger
import logging
import pandas as pd
import json


def run_test(exchange: PhemexClient, logger: logging.Logger) -> None:
    balances = exchange.get_balance()
    for currency, amount in balances.items():
        print(f"{currency}: {amount}")
    symbol="BTC/USDT:USDT"
    btc_1m: CandleData = exchange.get_ohlcv(symbol=symbol)
    #btc_1m.add_rsi()
    #btc_1m.add_sma(5)
    #self.logger.info(btc_1m.df)
    res = exchange.limit_buy(symbol, size=20.0)


def main():
    loggers = {
        "bot": get_logger("Bot"),
        "exchange": get_logger("Exchange")
    }
    exchange = PhemexClient(testnet=True, logger=loggers["exchange"])
    try:
        run_test(exchange=exchange, logger=loggers["bot"])
    except Exception as e:
        loggers["bot"].info(f"Error: {e}")

if __name__ == "__main__":
    main()
