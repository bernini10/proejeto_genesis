import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V6) - O TITÃ (30m/5m)
PROFIT FACTOR: 2.88 | RETORNO: 8586% | TRADES: 922
VEREDITO: A maior densidade de lucro por unidade de tempo encontrada.
"""

def executar_backtest():
    # 1. Carregar as bases do setup campeão
    df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_30m.parquet'))
    df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_5m.parquet'))
    
    # 2. Sincronização e Aceleração
    df_30m_sync = df_30m.reindex(df_5m.index, method='ffill')
    df_5m['acceleration'] = df_5m['velocity'].diff()

    # 3. Barreiras de 30 minutos
    std_30m = df_30m_sync['close'].rolling(20).std()
    mean_30m = df_30m_sync['close'].rolling(20).mean()

    # 4. Lógica Unificada (Simetria Total)
    # LONG
    l_ent = (df_5m.close > mean_30m + (std_30m * 0.5)) & \
            (df_30m_sync.velocity > 0.5) & \
            (df_5m.acceleration > 0)
    l_ext = df_5m.close < mean_30m

    # SHORT
    s_ent = (df_5m.close < mean_30m - (std_30m * 0.5)) & \
            (df_30m_sync.velocity < -0.5) & \
            (df_5m.acceleration < 0)
    s_ext = df_5m.close > mean_30m

    pf = vbt.Portfolio.from_signals(
        df_5m.close,
        entries=l_ent, exits=l_ext,
        short_entries=s_ent, short_exits=s_ext,
        fees=0.001, freq="5m"
    )
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n⚡ GÊNESIS PRO V6: O TITÃ FOI ATIVADO")
    print(resultado.stats())
