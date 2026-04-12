import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Carregar Dimensões Proporcionais
print("📡 Sincronizando Fractal: Macro (30m) e Micro (5m)...")
df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_30m.parquet'))
df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_5m.parquet'))

# 2. Sincronizar Micro com Macro (Zoom)
df_30m_sync = df_30m.reindex(df_5m.index, method='ffill')

# 3. Lei da Barreira no 30m
window = 20
df_30m_sync['upper_wall'] = df_30m_sync['close'].rolling(window).mean() + (df_30m_sync['close'].rolling(window).std() * 2)

# 4. Regra de Entrada: Ruptura no 30m + Confirmação no 5m
entries = (df_5m['close'] > df_30m_sync['upper_wall']) & \
          (df_30m_sync['velocity'] > 0.5) & \
          (df_5m['velocity'] > 0.3)

# 5. Saída: Perda de Tensão (Preço volta para a média do 30m)
exits = df_5m['close'] < df_30m_sync['close'].rolling(window).mean()

# 6. Backtest
pf = vbt.Portfolio.from_signals(df_5m.close, entries, exits, fees=0.001, freq="5m")

print("\n📊 RESULTADO FRACTAL (30m / 5m):")
print(pf.stats())
