import pandas as pd
from core.physics import pipeline_fisica

df_30m = pipeline_fisica(pd.read_parquet('data/ohlcv/ETH_USDT_30m.parquet'))
df_5m = pipeline_fisica(pd.read_parquet('data/ohlcv/ETH_USDT_5m.parquet'))

print("📊 ESTATÍSTICAS DE VETORES (ETH):")
print(f"Velocidade Máxima (30m): {df_30m['velocity'].max():.4f}")
print(f"Velocidade Mínima (30m): {df_30m['velocity'].min():.4f}")
print(f"Velocidade Média (30m):  {df_30m['velocity'].mean():.4f}")

# Verificar se a condição velocity > 0.5 alguma vez é verdadeira
possuem_velocidade = (df_30m['velocity'] > 0.5).sum()
print(f"\nSinais de Velocidade > 0.5 encontrados: {possuem_velocidade}")
