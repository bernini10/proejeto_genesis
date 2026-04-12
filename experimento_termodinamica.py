import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

# 1. Carregar Base Doppler (v3)
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))
df_15m['acceleration'] = df_15m['velocity'].diff()
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 2. Barreira Adaptativa (Relatividade de Severino)
v_media = df_1h_sync['volume'].rolling(50).mean()
massa_relativa = df_1h_sync['volume'] / v_media
sigma_multi = massa_relativa.apply(lambda x: 1.5 if x > 1.5 else 2.5)
std_1h = df_1h_sync['close'].rolling(20).std()
mean_1h = df_1h_sync['close'].rolling(20).mean()
dynamic_wall = mean_1h + (std_1h * sigma_multi)

# 3. Regras de Entrada e Saída Base
entries = (df_15m['close'] > dynamic_wall) & \
          (df_1h_sync['velocity'] > 0.5) & \
          (df_15m['acceleration'] > 0)
exits = df_15m['close'] < mean_1h

# 4. Implementação Manual do Cool-off (Termodinâmica Pura)
# Criamos um filtro que ignora sinais por 24 candles após o último sinal aceito
raw_entries = entries.values
cooldown_entries = np.zeros_like(raw_entries, dtype=bool)
last_entry_idx = -25  # Inicializa para permitir o primeiro sinal

for i in range(len(raw_entries)):
    if raw_entries[i] and (i - last_entry_idx >= 24):
        cooldown_entries[i] = True
        last_entry_idx = i

# Converter de volta para Series para processar no VectorBT
cooldown_series = pd.Series(cooldown_entries, index=entries.index)

# 5. Execução do Backtest
pf = vbt.Portfolio.from_signals(
    df_15m.close, 
    cooldown_series, 
    exits, 
    fees=0.001, 
    freq="15m"
)

print("\n📊 RESULTADO: TERMODINÂMICA (RESFRIAMENTO MANUAL)")
print(pf.stats())
