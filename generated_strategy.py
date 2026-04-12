from core.physics import pipeline_fisica
import pandas as pd
import vectorbt as vbt

# Carregar dados
df = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')

# Aplicar pipeline físico
df = pipeline_fisica(df)

# Criar sinais de entrada e saída
entries = (df['velocity'] > 0.5) & (df['inertia'] >= 4) & (df['pressure_balance'] > 0)
exits = df['velocity'] < -0.1

# Realizar backtest
portfolio = vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="1H")

# Retornar resultado do backtest
print(portfolio.stats())