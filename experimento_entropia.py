import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

df = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
df = pipeline_fisica(df)

# 1. Cálculo de Momento (P)
df['momentum_p'] = df['volume'] * df['velocity']

# 2. Cálculo de Entropia (Eficiência de Deslocamento)
lookback = 5
deslocamento = (df['close'] - df['close'].shift(lookback)).abs()
distancia = (df['high'] - df['low']).rolling(lookback).sum()
# Eficiência: 1 = Linha reta (Ordem), 0 = Vai e volta (Caos)
df['eficiencia'] = deslocamento / distancia

# 3. Regra de Entrada: Momento COM Ordem
v_media = df['volume'].rolling(50).mean()
# Só entra se: Velocidade > 0.5 + Volume Forte + Movimento Ordenado (Eficiência > 0.6)
entries = (df['velocity'] > 0.5) & \
          (df['volume'] > v_media * 1.5) & \
          (df['eficiencia'] > 0.6)

# 4. Saída: Inversão de Momento
exits = df['momentum_p'] < 0

pf = vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="1h")

print("\n📊 RESULTADO: MOMENTO LINEAR + FILTRO DE ENTROPIA (ORDEM)")
print(pf.stats())
