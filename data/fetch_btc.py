import ccxt, pandas as pd, time
from pathlib import Path

EXCHANGE = 'binance'
SYMBOL = 'BTC/USDT'
TIMEFRAMES = ['1m','5m','15m','30m','1h','4h','12h']
DATA_DIR = Path('data/ohlcv')
DATA_DIR.mkdir(parents=True, exist_ok=True)
exchange = ccxt.binance({'enableRateLimit': True})

for tf in TIMEFRAMES:
    file = DATA_DIR / f"{SYMBOL.replace('/', '_')}_{tf}.parquet"
    if file.exists():
        print(f'✅ {tf} ja existe')
        continue
    print(f'📥 Baixando {tf}...')
    since = exchange.parse8601('2020-01-01T00:00:00Z')
    all_candles = []
    while True:
        ohlcv = exchange.fetch_ohlcv(SYMBOL, tf, since=since, limit=1000)
        if not ohlcv: break
        all_candles.extend(ohlcv)
        since = ohlcv[-1][0] + 1
        time.sleep(0.3)
    df = pd.DataFrame(all_candles, columns=['timestamp','open','high','low','close','volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.to_parquet(file, engine='pyarrow')
    print(f'💾 Salvo {file} ({len(df)} candles)')
