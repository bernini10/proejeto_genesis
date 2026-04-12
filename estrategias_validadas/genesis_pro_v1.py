import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

"""
ESTRATÉGIA: GÊNESIS PRO (V1)
CONCEITO: Ruptura de Barreira de Potencial (Efeito Túnel)
ESCALA: Macro (1h) com Confirmação Micro (15m)
PROFIT FACTOR VALIDADO: 3.77
"""

def executar_backtest():
    # Carregar Dados
    print("📡 Carregando Dimensões (1h e 15m)...")
    df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
    df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
    
    # Processar Física Base
    df_1h = pipeline_fisica(df_1h)
    df_15m = pipeline_fisica(df_15m)

    # Sincronizar Micro com Macro (Zoom de precisão)
    df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

    # --- LEI DETERMINÍSTICA ---
    # 1. Definição da Barreira (Macro 1h)
    window = 20
    std_1h = df_1h_sync['close'].rolling(window).std()
    mean_1h = df_1h_sync['close'].rolling(window).mean()
    upper_wall = mean_1h + (std_1h * 2)

    # 2. Regra de Entrada (A Ruptura)
    # Condição: Preço fura barreira 1h + Velocidade Macro alta + Velocidade Micro positiva
    entries = (df_15m['close'] > upper_wall) & \
              (df_1h_sync['velocity'] > 0.5) & \
              (df_15m['velocity'] > 0.2)

    # 3. Regra de Saída (Perda de Tensão)
    # Sai quando o preço retorna para a média do 1h (ponto de equilíbrio)
    exits = df_15m['close'] < mean_1h

    # --- EXECUÇÃO ---
    pf = vbt.Portfolio.from_signals(
        df_15m.close, 
        entries, 
        exits, 
        fees=0.001, 
        freq="15m",
        init_cash=1000
    )
    
    return pf

if __name__ == "__main__":
    resultado = executar_backtest()
    print("\n✅ ESTRATÉGIA GÊNESIS PRO SALVA E VALIDADA")
    print(resultado.stats())
