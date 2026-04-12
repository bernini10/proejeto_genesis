import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

# 1. Preparação dos Dados
print("📡 Auditando Motores de Física...")
df_1h = pd.read_parquet('data/ohlcv/BTC_USDT_1h.parquet')
df_15m = pd.read_parquet('data/ohlcv/BTC_USDT_15m.parquet')

df_1h = pipeline_fisica(df_1h)
df_15m = pipeline_fisica(df_15m)
df_1h_sync = df_1h.reindex(df_15m.index, method='ffill')

def rodar_teste(nome, sigma, usar_fisica):
    std_1h = df_1h_sync['close'].rolling(20).std()
    mean_1h = df_1h_sync['close'].rolling(20).mean()
    wall = mean_1h + (std_1h * sigma)
    
    if usar_fisica:
        # Filtro de Velocidade
        entries = (df_15m['close'] > wall) & (df_1h_sync['velocity'] > 0.5)
    else:
        # Sem filtro nenhum
        entries = (df_15m['close'] > wall)
        
    exits = df_15m['close'] < mean_1h
    
    pf = vbt.Portfolio.from_signals(df_15m.close, entries, exits, fees=0.001, freq="15m")
    
    # Usar .stats() para evitar erros de atributo
    stats = pf.stats()
    
    print(f"\n--- {nome} ---")
    print(f"Total de Trades: {stats['Total Trades']}")
    print(f"Profit Factor:   {stats['Profit Factor']:.2f}")
    print(f"Retorno Total:   {stats['Total Return [%]']:.2f}%")

# RODANDO OS 3 CENÁRIOS
try:
    rodar_teste("CONTROLE (1h/15m)", 2.0, True)
    rodar_teste("AGRESSIVO (PAREDE FINA)", 0.5, True)
    rodar_teste("BRUTO (SEM FILTRO VELOCIDADE)", 2.0, False)
except Exception as e:
    print(f"\n❌ Erro na Auditoria: {e}")
