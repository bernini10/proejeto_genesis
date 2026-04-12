import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# Carregar Dimensões
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))

# Sincronizar Micro com Macro
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 1. Lei da Barreira (1h)
window = 20
df_1h_sync['std'] = df_1h_sync['close'].rolling(window).mean() # Simplificado para o sync
df_1h_sync['upper_wall'] = df_1h_sync['close'].rolling(window).mean() + (df_1h_sync['close'].rolling(window).std() * 2)

# 2. Regra Gênesis Pro: Ruptura Macro + Confirmação Micro
entries = (df_15m['close'] > df_1h_sync['upper_wall']) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['velocity'] > 0.2)

# 3. Saída: Perda de Tensão (Preço volta para média do 1h)
exits = df_15m['close'] < df_1h_sync['close'].rolling(window).mean()

pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")

print("\n📊 RESULTADO FINAL: GÊNESIS PRO (O Salto Multidimensional)")
print(pf.stats())
