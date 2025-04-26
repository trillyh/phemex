import pandas as pd
from ta.momentum import RSIIndicator
import time
class CandleData:
    def __init__(self, df, symbol, timeframe):
        self.df = df
        self.symbol = symbol
        self.timeframe = timeframe

    # private function, convert timeframe to minutes
    def _timeframe_to_minutes(self):
        units = {"m": 1, "h": 60, "d": 1440}
        for unit in units:
            if self.timeframe.endswith(unit):
                return int(self.timeframe[:-1]) * units[unit]
        raise ValueError(f"Unknown timeframe format: {self.timeframe}")

    def add_sma(self, period):
        start = time.perf_counter()

        tf_minutes = self._timeframe_to_minutes()
        sma_duration_min = period * tf_minutes

        if len(self.df) < period:
            raise ValueError(f"SMA{period} requires at least {period} rows, but only {len(self.df)} rows available.")

        if sma_duration_min > 60 * 24 * 7: # larger than 7 day of data
            print(f"⚠️ Warning: SMA{period} spans {sma_duration_min} minutes (~{sma_duration_min//1440:.1f} days), which might be too long for the {self.timeframe} candles you have.")
        self.df[f"sma{period}"] = self.df["close"].rolling(window=period).mean()

        end = time.perf_counter()
        print(f"Added SMA (Took {(end-start)} secs)")

    def add_rsi(self):
        start = time.perf_counter()

        rsi = RSIIndicator(self.df["close"])
        self.df['rsi'] = rsi.rsi()

        end = time.perf_counter()
        print(f"Added RSI (Took {(end-start)} secs)")

    def add_vwap(self):
        ...


