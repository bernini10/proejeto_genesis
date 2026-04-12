import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

def motor_tita_eth():
    df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/ETH_USDT_30m.parquet'))
    df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/ETH_USDT_5m.parquet'))
    
    df_30m_sync = df_30m.reindex(df_5m.index, method='ffill')
    df_5m['acceleration'] = df_5m['velocity'].diff()

    std_30m = df_30m_sync['close'].rolling(20).std()
    mean_30m = df_30m_sync['close'].rolling(20).mean()

    # SENSIBILIDADE CALIBRADA PARA ETH
    sens = 0.02

    l_ent = (df_5m.close > mean_30m + (std_30m * 0.5)) & (df_30m_sync.velocity > sens) & (df_5m.acceleration > 0)
    l_ext = df_5m.close < mean_30m

    s_ent = (df_5m.close < mean_30m - (std_30m * 0.5)) & (df_30m_sync.velocity < -sens) & (df_5m.acceleration < 0)
    s_ext = df_5m.close > mean_30m

    pf = vbt.Portfolio.from_signals(
        df_5m.close,
        entries=l_ent, exits=l_ext,
        short_entries=s_ent, short_exits=s_ext,
        fees=0.001, freq="5m"
    )
    return pf

if __name__ == "__main__":
    resultado = motor_tita_eth()
    print("🏆 ETH TITÃ: O PODER DA FLUIDEZ")
    print(resultado.stats())
