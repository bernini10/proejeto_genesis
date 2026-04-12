import pandas as pd
import vectorbt as vbt
import itertools
from core.physics import pipeline_fisica

# Timeframes disponíveis (ajuste se faltar algum no seu VPS)
tfs = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '12h', '1d']

# Função de conversão para minutos (para garantir que Âncora > Execução)
def to_min(tf):
    units = {'m': 1, 'h': 60, 'd': 1440}
    return int(tf[:-1]) * units[tf[-1]]

combinacoes = [(a, e) for a, e in itertools.permutations(tfs, 2) if to_min(a) > to_min(e)]

resultados = []
print(f"🔬 Iniciando Varredura de {len(combinacoes)} combinações binárias...")

for anc, exe in combinacoes:
    try:
        df_anc = pipeline_fisica(pd.read_parquet(f'data/ohlcv/BTC_USDT_{anc}.parquet'))
        df_exe = pipeline_fisica(pd.read_parquet(f'data/ohlcv/BTC_USDT_{exe}.parquet'))
        
        df_anc_sync = df_anc.reindex(df_exe.index, method='ffill')
        df_exe['acceleration'] = df_exe['velocity'].diff()
        
        std_anc = df_anc_sync['close'].rolling(20).std()
        mean_anc = df_anc_sync['close'].rolling(20).mean()

        # Lógica Gênesis Pro v5
        l_ent = (df_exe.close > mean_anc + (std_anc * 0.5)) & (df_anc_sync.velocity > 0.5) & (df_exe.acceleration > 0)
        l_ext = df_exe.close < mean_anc
        s_ent = (df_exe.close < mean_anc - (std_anc * 0.5)) & (df_anc_sync.velocity < -0.5) & (df_exe.acceleration < 0)
        s_ext = df_exe.close > mean_anc

        pf = vbt.Portfolio.from_signals(df_exe.close, entries=l_ent, exits=l_ext, 
                                        short_entries=s_ent, short_exits=s_ext, fees=0.001)
        
        stats = pf.stats()
        resultados.append({
            "Setup": f"{anc}/{exe}",
            "Trades": int(stats['Total Trades']),
            "WinRate": f"{stats['Win Rate [%]']:.1f}%",
            "PF": round(stats['Profit Factor'], 2),
            "Return": round(stats['Total Return [%]'], 2),
            "Expectancy": round(stats['Expectancy'], 4)
        })
    except:
        continue

df_res = pd.DataFrame(resultados).sort_values(by="Return", ascending=False)
print("\n🏆 RANKING DE EFICIÊNCIA BINÁRIA:")
print(df_res.to_string(index=False))
