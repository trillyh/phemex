import ccxt
from typing import Dict, cast
from config import PHEMEX_API_KEY, PHEMEX_API_SECRET
from logger import get_logger
import time
import pandas as pd
from candle import CandleData
from typing import Optional
import logging
from logger import get_logger


class PhemexClient:
    def __init__(self, testnet=False, logger:Optional[logging.Logger]=None):
        start = time.perf_counter()
        self._exchange = ccxt.phemex({
            'apiKey': cast(str, PHEMEX_API_KEY),
            'secret': cast(str, PHEMEX_API_SECRET),
            'enableRateLimit': True,
            'timeout': 10000, # be careful
        })
        self._exchange.set_sandbox_mode(testnet) # activates testnet mode
        self.logger = logger or get_logger("Exchange")

        self._exchange.load_markets()
        end = time.perf_counter()
        self.logger.info(f"Loaded market, took {end-start}")

    def buy(self, symbol: str):
        orderbook = self._exchange.fetch_order_book(symbol)
        return orderbook


    def get_balance(self) -> Dict[str, float]:
        try:
            start = time.perf_counter()

            balance_data = self._exchange.fetch_balance()
            total_balances = balance_data['total']

            end = time.perf_counter()

            self.logger.info(f"Sucessfully fetched balance (Took {end-start})")
            return {k: float(v) for k, v in total_balances.items() if isinstance(v, (int, float)) and v > 0}
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            raise

    # return a CandleData instance
    def get_ohlcv(self, symbol:str = "BTC/USDT", timeframe: str= "1m", limit:int =100) -> CandleData:
        candles = self._exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # set timestamp as col
        df.set_index("timestamp", inplace=True)
        return CandleData(df=df, symbol=symbol, timeframe=timeframe)
