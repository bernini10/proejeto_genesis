import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Carregar a Base Vencedora (v3 Doppler)
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))

df_15m['acceleration'] = df_15m['velocity'].diff()
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 2. Configuração de Barreira Adaptativa (v3)
v_media = df_1h_sync['volume'].rolling(50).mean()
massa_relativa = df_1h_sync['volume'] / v_media
sigma_multi = massa_relativa.apply(lambda x: 1.5 if x > 1.5 else 2.5)

std_1h = df_1h_sync['close'].rolling(20).std()
mean_1h = df_1h_sync['close'].rolling(20).mean()
dynamic_wall = mean_1h + (std_1h * sigma_multi)

# 3. Gatilho de Exaustão (O Ponto de Retorno do Atrator)
# Se o preço bater em 4 sigmas, a energia acabou.
exhaustion_wall = mean_1h + (std_1h * 4)

# 4. Regras de Entrada
entries = (df_15m['close'] > dynamic_wall) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['acceleration'] > 0)

# 5. Regras de Saída (Dupla): Retorno à Média OU Exaustão Cinética
exits = (df_15m['close'] < mean_1h) | (df_15m['close'] >= exhaustion_wall)

pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")

print("\n📊 RESULTADO: TEORIA DO CAOS (SAÍDA POR EXAUSTÃO)")
print(pf.stats())
