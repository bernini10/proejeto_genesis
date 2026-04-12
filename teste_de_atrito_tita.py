import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

def testar_com_atrito():
    df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_30m.parquet'))
    df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_5m.parquet'))
    df_30m_sync = df_30m.reindex(df_5m.index, method='ffill')
    df_5m['acceleration'] = df_5m['velocity'].diff()
    
    std_30m = df_30m_sync['close'].rolling(20).std()
    mean_30m = df_30m_sync['close'].rolling(20).mean()

    l_ent = (df_5m.close > mean_30m + (std_30m * 0.5)) & (df_30m_sync.velocity > 0.5) & (df_5m.acceleration > 0)
    l_ext = df_5m.close < mean_30m
    s_ent = (df_5m.close < mean_30m - (std_30m * 0.5)) & (df_30m_sync.velocity < -0.5) & (df_5m.acceleration < 0)
    s_ext = df_5m.close > mean_30m

    # AQUI ESTÁ O TESTE DE FOGO: 0.1% de taxa + 0.1% de slippage = 0.002 total
    pf_realista = vbt.Portfolio.from_signals(
        df_5m.close,
        entries=l_ent, exits=l_ext,
        short_entries=s_ent, short_exits=s_ext,
        fees=0.002, 
        freq="5m"
    )
    
    print("\n🌪️ TESTE DE ATRITO (TAXAS DOBRADAS - SIMULANDO SLIPPAGE)")
    print(f"Retorno Final: {pf_realista.total_return() * 100:.2f}%")
    print(f"Profit Factor: {pf_realista.profit_factor:.2f}")

if __name__ == "__main__":
    testar_com_atrito()
