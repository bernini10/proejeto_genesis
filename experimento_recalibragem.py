import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 1. Barreira Sensível (O aprendizado do teste de certeza)
std_1h = df_1h_sync['close'].rolling(20).std()
mean_1h = df_1h_sync['close'].rolling(20).mean()
wall = mean_1h + (std_1h * 0.5) # Válvula aberta

# 2. Física de Refino (Massa e Aceleração)
df_15m['acceleration'] = df_15m['velocity'].diff()
v_media = df_1h_sync['volume'].rolling(50).mean()

# Regra: Barreira Aberta + Massa Mínima + Aceleração Real
entries = (df_15m['close'] > wall) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['acceleration'] > 0) & \
          (df_1h_sync['volume'] > v_media * 0.8) # Não precisa ser volume gigante, apenas real

exits = df_15m['close'] < mean_1h

pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")
print("\n📊 RESULTADO: GÊNESIS RECALIBRADO (ALTA FREQUÊNCIA)")
print(pf.stats())
