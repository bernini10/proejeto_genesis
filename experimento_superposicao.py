import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

def carregar_e_processar(path):
    df = pd.read_parquet(path)
    return pipeline_fisica(df)

# 1. Carregar as 3 Dimensões
print("📡 Sincronizando dimensões (15m, 1h, 4h)...")
df_15m = carregar_e_processar('data/ohlcv/BTC_USDT_15m.parquet')
df_1h = carregar_e_processar('data/ohlcv/BTC_USDT_1h.parquet')
df_4h = carregar_e_processar('data/ohlcv/BTC_USDT_4h.parquet')

# 2. Alinhamento de Índices (Garantir que estamos comparando o mesmo tempo)
# Vamos usar o índice do 15m como base e trazer o estado das ondas maiores
df_1h_resampled = df_1h.reindex(df_15m.index, method='ffill')
df_4h_resampled = df_4h.reindex(df_15m.index, method='ffill')

# 3. Definição da Superposição (Interferência Construtiva)
# A regra determinística: Vel_Micro > 0 E Vel_Medio > 0 E Vel_Macro > 0
entries = (df_15m['velocity'] > 0.3) & \
          (df_1h_resampled['velocity'] > 0) & \
          (df_4h_resampled['velocity'] > 0) & \
          (df_15m['inertia'] >= 3)

# Saída: Quando a onda micro perde a fase (Velocidade inverte no 15m)
exits = df_15m['velocity'] < 0

# 4. Execução do Backtest com Taxas Reais
pf = vbt.Portfolio.from_signals(
    df_15m.close, 
    entries, 
    exits, 
    fees=0.001, 
    freq="15m",
    init_cash=1000
)

print("\n📊 RESULTADO DO EXPERIMENTO DE SUPERPOSIÇÃO:")
print(pf.stats())
