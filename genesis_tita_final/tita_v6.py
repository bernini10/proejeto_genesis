import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

def motor_tita():
    """
    Motor Principal do Gênesis Pro v6
    Âncora: 30m | Execução: 5m
    """
    df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_30m.parquet'))
    df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_5m.parquet'))
    
    df_30m_sync = df_30m.reindex(df_5m.index, method='ffill')
    df_5m['acceleration'] = df_5m['velocity'].diff()

    std_30m = df_30m_sync['close'].rolling(20).std()
    mean_30m = df_30m_sync['close'].rolling(20).mean()

    # Lógica de Lei Determinística
    long_entries = (df_5m.close > mean_30m + (std_30m * 0.5)) & (df_30m_sync.velocity > 0.5) & (df_5m.acceleration > 0)
    long_exits = df_5m.close < mean_30m

    short_entries = (df_5m.close < mean_30m - (std_30m * 0.5)) & (df_30m_sync.velocity < -0.5) & (df_5m.acceleration < 0)
    short_exits = df_5m.close > mean_30m

    pf = vbt.Portfolio.from_signals(
        df_5m.close,
        entries=long_entries, exits=long_exits,
        short_entries=short_entries, short_exits=short_exits,
        fees=0.001, freq="5m"
    )
    return pf

if __name__ == "__main__":
    resultado = motor_tita()
    print(resultado.stats())
