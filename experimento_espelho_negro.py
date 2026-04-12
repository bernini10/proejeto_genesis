import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Preparação dos Dados
df_1h = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet'))
df_15m = pipeline_fisica(pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet'))

df_15m['acceleration'] = df_15m['velocity'].diff()
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

# 2. Definição da Barreira de Queda
std_1h = df_1h_sync['close'].rolling(20).std()
mean_1h = df_1h_sync['close'].rolling(20).mean()
lower_wall = mean_1h - (std_1h * 0.5)

# 3. Regras de Short (Entrada e Saída)
# Entramos quando o preço fura o suporte com velocidade e aceleração negativas
short_entries = (df_15m['close'] < lower_wall) & \
                (df_1h_sync['velocity'] < -0.5) & \
                (df_15m['acceleration'] < 0)

# Saímos quando o preço volta para a média (recuperação de equilíbrio)
short_exits = df_15m['close'] > mean_1h

# 4. Backtest (Configuração correta para a sua versão do vbt)
pf = vbt.Portfolio.from_signals(
    df_15m.close, 
    entries=None,        # Vazio para Longs
    exits=None,          # Vazio para Longs
    short_entries=short_entries, 
    short_exits=short_exits, 
    fees=0.001, 
    freq="15m"
)

print("\n🌑 RESULTADO: ESPELHO NEGRO (SHORTS - SÓ QUEDA)")
print(pf.stats())
