import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

df = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
df = pipeline_fisica(df)

# 1. Definir a Barreira (Volatilidade Estática)
# Usamos o Desvio Padrão para medir a "grossura" da parede
df['std'] = df['close'].rolling(20).std()
df['upper_wall'] = df['close'].rolling(20).mean() + (df['std'] * 2)

# 2. Regra de Entrada: Efeito Túnel
# Só entramos se o Preço furar a "parede" COM Velocidade e Pressão positiva
entries = (df['close'] > df['upper_wall']) & \
          (df['velocity'] > 0.5) & \
          (df['pressure_balance'] > 0)

# 3. Saída: Inversão de Polaridade (Quando o preço volta para dentro da barreira)
exits = df['close'] < df['upper_wall']

pf = vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="1h")

print("\n📊 RESULTADO: EFEITO TÚNEL (BARREIRA DE POTENCIAL)")
print(pf.stats())
