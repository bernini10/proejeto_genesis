import ccxt
import pandas as pd
import time

exchange = ccxt.binance()
symbol = 'ETH/USDT'
timeframes = ['1h', '30m', '15m', '5m', '1m']
since = exchange.parse8601('2020-01-01T00:00:00Z')

for tf in timeframes:
    print(f"📡 Aspirando histórico total de {tf}...")
    all_ohlcv = []
    current_since = since
    
    while True:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, tf, since=current_since, limit=1000)
            if not ohlcv:
                break
            current_since = ohlcv[-1][0] + 1
            all_ohlcv.extend(ohlcv)
            
            # Feedback de progresso
            if len(all_ohlcv) % 5000 == 0:
                print(f"   > {len(all_ohlcv)} velas capturadas...")
                
            if len(ohlcv) < 1000:
                break
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            print(f"⚠️ Erro: {e}. Tentando novamente...")
            time.sleep(5)

    df = pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df.to_parquet(f"data/ohlcv/ETH_USDT_{tf}.parquet")
    print(f"✅ {tf} finalizado com {len(df)} velas.\n")

