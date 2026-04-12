import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V4) - ALTA FREQUÊNCIA FÍSICA
CONCEITO: Válvula de 0.5 Sigma + Vetores de Aceleração
PROFIT FACTOR: 4.48 | WIN RATE: 70.5% | TRADES: 51
VEREDITO: A maior eficiência energética encontrada no BTC 1h/15m.
"""

def executar_backtest():
    df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
    df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
    
    df_1h = pipeline_fisica(df_1h)
    df_15m = pipeline_fisica(df_15m)
    df_15m['acceleration'] = df_15m['velocity'].diff()
    df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

    # Configuração de Barreira Sensível (A Descoberta do Mestre)
    std_1h = df_1h_sync['close'].rolling(20).std()
    mean_1h = df_1h_sync['close'].rolling(20).mean()
    wall = mean_1h + (std_1h * 0.5) 
    
    # Filtro de Massa Relativa
    v_media = df_1h_sync['volume'].rolling(50).mean()

    # Regras de Entrada
    entries = (df_15m['close'] > wall) & \
              (df_1h_sync['velocity'] > 0.5) & \
              (df_15m['acceleration'] > 0) & \
              (df_1h_sync['volume'] > v_media * 0.8)
              
    exits = df_15m['close'] < mean_1h

    pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n👑 GÊNESIS PRO V4 SALVO (VERSÃO DEFINITIVA)")
    print(resultado.stats())
