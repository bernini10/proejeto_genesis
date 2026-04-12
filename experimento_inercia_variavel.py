import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Carregar Base
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 2. Cálculo da "Massa" (Volume Relativo)
v_media = df_1h_sync['volume'].rolling(50).mean()
df_1h_sync['massa_relativa'] = df_1h_sync['volume'] / v_media

# 3. Barreira Adaptativa (Relatividade de Severino)
# Se a massa for alta (> 1.5x média), a parede encolhe para 1.5 DP.
# Se a massa for baixa, a parede sobe para 2.5 DP.
df_1h_sync['sigma_multi'] = df_1h_sync['massa_relativa'].apply(lambda x: 1.5 if x > 1.5 else 2.5)

std_1h = df_1h_sync['close'].rolling(20).std()
mean_1h = df_1h_sync['close'].rolling(20).mean()
df_1h_sync['dynamic_wall'] = mean_1h + (std_1h * df_1h_sync['sigma_multi'])

# 4. Regra de Entrada
entries = (df_15m['close'] > df_1h_sync['dynamic_wall']) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['velocity'] > 0.2)

exits = df_15m['close'] < mean_1h

pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")

print("\n📊 RESULTADO: RELATIVIDADE DA INÉRCIA (BARREIRA ADAPTATIVA)")
print(pf.stats())
