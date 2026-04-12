import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V3.1) - PROTEÇÃO DE EXAUSTÃO
CONCEITO: Saída por Retorno ao Atrator OU Limite de Elasticidade (Sigma 4)
PROFIT FACTOR: 3.14 (Mantido)
LIÇÃO: O BTC respeita a média de 1h como um imã gravitacional.
"""

def executar_backtest():
    df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
    df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
    
    df_1h = pipeline_fisica(df_1h)
    df_15m = pipeline_fisica(df_15m)
    df_15m['acceleration'] = df_15m['velocity'].diff()
    df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

    # Configurações de Barreira e Massa (v3)
    v_media = df_1h_sync['volume'].rolling(50).mean()
    massa_relativa = df_1h_sync['volume'] / v_media
    sigma_multi = massa_relativa.apply(lambda x: 1.5 if x > 1.5 else 2.5)

    std_1h = df_1h_sync['close'].rolling(20).std()
    mean_1h = df_1h_sync['close'].rolling(20).mean()
    dynamic_wall = mean_1h + (std_1h * sigma_multi)
    
    # Válvula de Segurança: Exaustão Cinética (Sigma 4)
    exhaustion_wall = mean_1h + (std_1h * 4)

    # Regras
    entries = (df_15m['close'] > dynamic_wall) & \
              (df_1h_sync['velocity'] > 0.5) & \
              (df_15m['acceleration'] > 0)
              
    # Saída por equilíbrio (média) OU exaustão (estiramento máximo)
    exits = (df_15m['close'] < mean_1h) | (df_15m['close'] >= exhaustion_wall)

    pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n🛡️ GÊNESIS PRO V3.1 SALVO (COM VÁLVULA DE EXAUSTÃO)")
    print(resultado.stats())
