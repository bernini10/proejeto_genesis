import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V5) - SIMETRIA TOTAL
PROFIT FACTOR: 3.40 | RETORNO: 237% | TRADES: 135
VEREDITO: O equilíbrio perfeito entre propulsão e gravidade.
"""

def executar_backtest():
    df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
    df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
    
    df_1h = pipeline_fisica(df_1h)
    df_15m = pipeline_fisica(df_15m)
    df_15m['acceleration'] = df_15m['velocity'].diff()
    df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

    std_1h = df_1h_sync['close'].rolling(20).std()
    mean_1h = df_1h_sync['close'].rolling(20).mean()

    # LONG
    long_entries = (df_15m['close'] > mean_1h + (std_1h * 0.5)) & \
                   (df_1h_sync['velocity'] > 0.5) & \
                   (df_15m['acceleration'] > 0)
    long_exits = df_15m['close'] < mean_1h

    # SHORT
    short_entries = (df_15m['close'] < mean_1h - (std_1h * 0.5)) & \
                    (df_1h_sync['velocity'] < -0.5) & \
                    (df_15m['acceleration'] < 0)
    short_exits = df_15m['close'] > mean_1h

    pf = vbt.Portfolio.from_signals(
        df_15m.close,
        entries=long_entries, exits=long_exits,
        short_entries=short_entries, short_exits=short_exits,
        fees=0.001, freq="15m"
    )
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n🏆 GÊNESIS PRO V5: O ÁPICE DA FÍSICA APLICADA")
    print(resultado.stats())
