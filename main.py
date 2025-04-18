from phemex_client import PhemexClient
from candle import CandleData

def main():
    exchange = PhemexClient(testnet=True)
    balances = exchange.get_balance()
    for currency, amount in balances.items():
        print(f"{currency}: {amount}")

    btc_1m: CandleData = exchange.get_ohlcv()
    btc_1m.add_rsi()
    btc_1m.add_sma(5)
    print(btc_1m.df)
if __name__ == "__main__":
    main()

