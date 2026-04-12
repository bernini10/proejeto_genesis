import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Carregar Base
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 2. Cálculo da Turbulência
window = 20
volatilidade = df_15m['close'].rolling(window).std()
# Aumentamos a sensibilidade: Aceitamos fluxos menos "perfeitos"
df_15m['laminaridade'] = df_15m['velocity'].abs() / (volatilidade + 1e-9)

# 3. Lei da Barreira
std_1h = df_1h_sync['close'].rolling(window).std()
mean_1h = df_1h_sync['close'].rolling(window).mean()
upper_wall = mean_1h + (std_1h * 2)

# 4. Regra: Agora com Filtro de Turbulência mais realista (> 0.01)
entries = (df_15m['close'] > upper_wall) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['velocity'] > 0.2) & \
          (df_15m['laminaridade'] > 0.01) # Reduzimos a exigência de pureza

exits = df_15m['close'] < mean_1h

pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")

print("\n📊 RESULTADO: DINÂMICA DE FLUIDOS (AJUSTE DE VISCOSIDADE)")
print(pf.stats())
