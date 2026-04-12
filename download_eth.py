import ccxt
import pandas as pd
import time

exchange = ccxt.binance()

def download_pair(symbol, timeframe):
    print(f"📡 Baixando {symbol} no timeframe {timeframe}...")
    all_ohlcv = []
    since = exchange.parse8601('2020-01-01T00:00:00Z')
    
    while True:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not ohlcv:
            break
        since = ohlcv[-1][0] + 1
        all_ohlcv.extend(ohlcv)
        time.sleep(exchange.rateLimit / 1000)
        if len(ohlcv) < 1000:
            break

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    
    filename = f"data/ohlcv/{symbol.replace('/', '_')}_{timeframe}.parquet"
    df.to_parquet(filename)
    print(f"✅ Salvo em: {filename}")

download_pair('ETH/USDT', '30m')
download_pair('ETH/USDT', '5m')
