import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V2) - RELATIVIDADE DA INÉRCIA
CONCEITO: Barreira de Potencial Adaptativa por Massa (Volume)
PROFIT FACTOR: 2.84 | WIN RATE: 60.5% | TRADES: 38
LIÇÃO: Massa (Volume) define a grossura da parede.
"""

def executar_backtest():
    # Carregar Dados
    df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
    df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
    
    # Processar Física
    df_1h = pipeline_fisica(df_1h)
    df_15m = pipeline_fisica(df_15m)
    df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

    # --- LEI DA RELATIVIDADE DE SEVERINO ---
    # Massa Relativa (Volume atual / Média)
    v_media = df_1h_sync['volume'].rolling(50).mean()
    massa_relativa = df_1h_sync['volume'] / v_media
    
    # Ajuste Dinâmico da Barreira (Sigma Multiplier)
    # Se tem massa, a parede é 1.5. Se não tem, é 2.5.
    sigma_multi = massa_relativa.apply(lambda x: 1.5 if x > 1.5 else 2.5)

    std_1h = df_1h_sync['close'].rolling(20).std()
    mean_1h = df_1h_sync['close'].rolling(20).mean()
    dynamic_wall = mean_1h + (std_1h * sigma_multi)

    # Regras de Entrada e Saída
    entries = (df_15m['close'] > dynamic_wall) & \
              (df_1h_sync['velocity'] > 0.5) & \
              (df_15m['velocity'] > 0.2)
              
    exits = df_15m['close'] < mean_1h

    pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n🚀 GÊNESIS PRO V2 SALVO (RELATIVIDADE)")
    print(resultado.stats())
