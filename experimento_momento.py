import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Carregar dados de 1h (Onde a massa e o movimento se equilibram melhor)
print("🔬 Carregando dados para Experimento de Momento Linear...")
df = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
df = pipeline_fisica(df)

# 2. Definir Momento (P = M * V)
# Massa = Volume / Velocidade = Preço_Change
df['momentum_p'] = df['volume'] * df['velocity']

# 3. Regra de Entrada: Força Impulsiva
# Só entramos se a Velocidade for alta E o Volume estiver acima da média (Massa confirmando)
v_media = df['volume'].rolling(50).mean()
entries = (df['velocity'] > 0.5) & (df['volume'] > v_media * 1.5)

# 4. Regra de Saída: Perda de Inércia
# Saímos quando o vetor de Momento inverte a polaridade
exits = df['momentum_p'] < 0

# 5. Backtest com realidade de taxas
pf = vbt.Portfolio.from_signals(
    df.close, 
    entries, 
    exits, 
    fees=0.001, 
    freq="1h",
    init_cash=1000
)

print("\n📊 RESULTADO: CONSERVAÇÃO DO MOMENTO (P = M * V)")
print(pf.stats())
