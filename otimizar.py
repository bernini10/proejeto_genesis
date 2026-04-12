import pandas as pd
import vectorbt as vbt
import numpy as np
from core.physics import pipeline_fisica

# 1. Preparação
df = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
df = pipeline_fisica(df)

# 2. Definir faixas de teste (Grid)
v_range = np.arange(0.1, 1.5, 0.2)
i_range = np.arange(2, 8, 1)

print(f"🔎 Iniciando Otimização em {len(v_range) * len(i_range)} combinações...")

results = []

for v in v_range:
    for i in i_range:
        entries = (df['velocity'] > v) & (df['inertia'] >= i) & (df['pressure_balance'] > 0)
        exits = (df['velocity'] < 0)
        
        pf = vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="1H")
        
        # O VectorBT entrega as métricas como uma Série através do .stats()
        pf_stats = pf.stats()
        
        results.append({
            'vel': round(v, 2),
            'iner': i,
            'profit_factor': pf_stats['Profit Factor'],
            'total_return': pf_stats['Total Return [%]'],
            'trades': pf_stats['Total Trades']
        })

# 3. Mostrar o Top 5
res_df = pd.DataFrame(results).dropna()
top_5 = res_df.sort_values(by='profit_factor', ascending=False).head(5)

print("\n🏆 TOP 5 ESTRATÉGIAS ENCONTRADAS:")
print(top_5.to_string(index=False))
