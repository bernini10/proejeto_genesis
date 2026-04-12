import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# Vamos testar no 15m para ver se a física se mantém na micro-escala
df = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')
df = pipeline_fisica(df)

# 1. Barreira Dinâmica mais sensível
window = 14 # Período menor = reação mais rápida
df['std'] = df['close'].rolling(window).std()
df['upper_wall'] = df['close'].rolling(window).mean() + (df['std'] * 1.8) # Parede mais fina

# 2. Regra de Entrada: Efeito Túnel Micro
entries = (df['close'] > df['upper_wall']) & \
          (df['velocity'] > 0.4) & \
          (df['pressure_balance'] > 0)

# 3. Saída: Inversão ou Trailing Stop Físico
exits = df['close'] < df['upper_wall']

pf = vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="15m")

print("\n📊 RESULTADO: RESSONÂNCIA NO MICRO (15M) - EFEITO TÚNEL")
print(pf.stats())
