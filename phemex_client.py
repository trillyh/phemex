import ccxt
import math
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

    # Given a cost, process the leverage based on min notional value
    # Then send the order -> return the order_id to the callee
    def limit_buy(self, symbol: str, size: float, leverage=1):
        orderbook = self._exchange.fetch_order_book(symbol)
        self._exchange.set_position_mode(hedged=False, symbol=symbol)
        price = 0.0
        amount = 0.0
        market = self._exchange.market(symbol)
        price_precision = convert_tick_to_precision(market['precision']['price'])
        amount_precision = convert_tick_to_precision(market['precision']['amount'])

        # TODO: check again in mainnet
        # hardcore this for now
        min_notional_crypto = 0.001
        try:
            best_ask = orderbook['asks'][0][0]
            tick_size = 1/10**price_precision
            price = round(best_ask - tick_size, price_precision)
            min_notional_usdt = min_notional_crypto * price
            amount = min_notional_crypto

            #contract_value = price_precision * price
            #contracts = size / contract_value
            #print(f"contracts: {contracts}")
    
            # means that i want this function to calculate the leverage
            if leverage == 1:
                leverage = round(min_notional_usdt / size)
        except Exception as e:
            print(f"Error when preprocessing limit buy order {e}")

        try:
            self.logger.info(f"trying to place order amount: {amount} price: {price} with lvg: {leverage}")
            self._exchange.set_leverage(leverage=leverage, symbol=symbol)
            order = self._exchange.create_limit_buy_order(

                symbol=symbol,
                amount=amount,
                price=price,
                params = {
                    #'timeInForce': 'PostOnly'
                }
            )
            order_id = order['info']['orderID']
            self.logger.info(f"Created order successfully {order_id}")
            return order_id

        except Exception as e:
            print(f"Error when creating limit buy order {e}")

    def cancel_all_orders(self, symbol: str):
        try:
            cancelled_orders = self._exchange.cancel_all_orders(symbol)
            self.logger.info(f"Cancelled all {len(cancelled_orders)} orders")
            return cancelled_orders
        except Exception as e:
            self.logger.warning(f"Failed to cancel all orders: {e}")

    def monitor_order_fill(self, symbol, order_id):
        order = self._exchange.fetch_order(order_id, symbol)
        filled = order['filled']
        remaining = order['remaining']
        status = order['status']

        print(f"Filled: {filled}, Remaining: {remaining}, Status: {status}")

        if status == "open" and remaining > 0:
            # Optionally cancel if stuck
            ...
            #print("Canceled remaining order")


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

def convert_tick_to_precision(tick_size: float) -> int:
    return abs(int(round(math.log10(tick_size))))
