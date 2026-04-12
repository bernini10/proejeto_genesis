import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica

def testar_combinacao(tf_ancora, tf_execucao):
    try:
        # Carregar bases
        path_ancora = f'data/ohlcv/BTC_USDT_{tf_ancora}.parquet'
        path_exec = f'data/ohlcv/BTC_USDT_{tf_execucao}.parquet'
        
        df_ancora = pipeline_fisica(pd.read_parquet(path_ancora))
        df_exec = pipeline_fisica(pd.read_parquet(path_exec))
        
        # Sincronização
        df_ancora_sync = df_ancora.reindex(df_exec.index, method='ffill')
        df_exec['acceleration'] = df_exec['velocity'].diff()
        
        # Física v5
        std_ancora = df_ancora_sync['close'].rolling(20).std()
        mean_ancora = df_ancora_sync['close'].rolling(20).mean()

        # Regras Unificadas (L+S)
        l_ent = (df_exec.close > mean_ancora + (std_ancora * 0.5)) & (df_ancora_sync.velocity > 0.5) & (df_exec.acceleration > 0)
        l_ext = df_exec.close < mean_ancora
        s_ent = (df_exec.close < mean_ancora - (std_ancora * 0.5)) & (df_ancora_sync.velocity < -0.5) & (df_exec.acceleration < 0)
        s_ext = df_exec.close > mean_ancora

        pf = vbt.Portfolio.from_signals(df_exec.close, entries=l_ent, exits=l_ext, 
                                        short_entries=s_ent, short_exits=s_ext, fees=0.001)
        
        return {
            "Par": f"{tf_ancora}/{tf_execucao}",
            "Trades": pf.trades.count(),
            "WinRate": pf.stats()['Win Rate [%]'],
            "PF": pf.stats()['Profit Factor'],
            "Return": pf.stats()['Total Return [%]']
        }
    except Exception:
        return None

# Lista de combinações para esgotar
combinacoes = [
    ("4h", "1h"), ("1h", "15m"), ("1h", "5m"), ("15m", "5m"), ("15m", "1m")
]

resultados = []
print("🧪 Iniciando Colisão de Timeframes...\n")

for anc, exe in combinacoes:
    res = testar_combinacao(anc, exe)
    if res:
        resultados.append(res)

df_res = pd.DataFrame(resultados).sort_values(by="Return", ascending=False)
print(df_res.to_string(index=False))
