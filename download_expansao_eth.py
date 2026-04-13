import ccxt
import pandas as pd
import time

exchange = ccxt.binance()
symbol = 'ETH/USDT'
timeframes = ['1h', '15m', '1m']

for tf in timeframes:
    print(f"📡 Baixando {tf}...")
    ohlcv = exchange.fetch_ohlcv(symbol, tf, since=exchange.parse8601('2022-01-01T00:00:00Z'), limit=5000)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.to_parquet(f"data/ohlcv/ETH_USDT_{tf}.parquet")
    time.sleep(1)
