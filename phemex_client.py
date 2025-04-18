import ccxt
from typing import Dict, cast
from config import PHEMEX_API_KEY, PHEMEX_API_SECRET
from logger import get_logger
import time
import pandas as pd
from candle import CandleData

logger = get_logger("PhemexClient")


class PhemexClient:
    def __init__(self, testnet=False):
        self.exchange = ccxt.phemex({
            'apiKey': cast(str, PHEMEX_API_KEY),
            'secret': cast(str, PHEMEX_API_SECRET),
            'enableRateLimit': True,
            'timeout': 10000, # be careful
        })
        self.exchange.set_sandbox_mode(testnet) # activates testnet mode

    def get_balance(self) -> Dict[str, float]:
        try:

            start = time.perf_counter()

            balance_data = self.exchange.fetch_balance()
            total_balances = balance_data['total']

            end = time.perf_counter()

            logger.info(f"Sucessfully fetched balance (Took {end-start})")
            return {k: float(v) for k, v in total_balances.items() if isinstance(v, (int, float)) and v > 0}
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise

    # return a CandleData instance
    def get_ohlcv(self, symbol:str = "BTC/USDT", timeframe: str= "1m", limit:int =100) -> CandleData:
        candles = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(candles, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # set timestamp as col
        df.set_index("timestamp", inplace=True)
        return CandleData(df=df, symbol=symbol, timeframe=timeframe)
