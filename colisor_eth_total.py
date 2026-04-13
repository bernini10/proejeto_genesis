import pandas as pd
import vectorbt as vbt
from core.physics import pipeline_fisica
import itertools

def rodar_colisor_eth():
    ancoras = ['1h', '30m', '15m']
    execucoes = ['15m', '5m', '1m']
    resultados = []
    
    print("\n🌪️  SUPER COLISOR TITÃ: TESTE DE RESSONÂNCIA")
    
    for tf_a, tf_e in itertools.product(ancoras, execucoes):
        if pd.Timedelta(tf_e) >= pd.Timedelta(tf_a): continue
            
        try:
            df_a = pipeline_fisica(pd.read_parquet(f'data/ohlcv/ETH_USDT_{tf_a}.parquet'))
            df_e = pipeline_fisica(pd.read_parquet(f'data/ohlcv/ETH_USDT_{tf_e}.parquet'))
            df_a_sync = df_a.reindex(df_e.index, method='ffill')
            df_e['acceleration'] = df_e['velocity'].diff()
            
            std_a = df_a_sync['close'].rolling(20).std()
            mean_a = df_a_sync['close'].rolling(20).mean()
            
            sens = 0.02
            l_ent = (df_e.close > mean_a + (std_a * 0.5)) & (df_a_sync.velocity > sens) & (df_e.acceleration > 0)
            l_ext = df_e.close < mean_a
            s_ent = (df_e.close < mean_a - (std_a * 0.5)) & (df_a_sync.velocity < -sens) & (df_e.acceleration < 0)
            s_ext = df_e.close > mean_a
            
            pf = vbt.Portfolio.from_signals(df_e.close, l_ent, l_ext, s_ent, s_ext, fees=0.001, freq=tf_e)
            
            # Correção aqui: Acessando stats de forma segura
            stats = pf.stats()
            resultados.append({
                'Config': f"{tf_a}/{tf_e}",
                'Retorno [%]': stats['Total Return [%]'],
                'PF': stats['Profit Factor'],
                'Trades': stats['Total Trades'],
                'WinRate [%]': stats['Win Rate [%]']
            })
            print(f"📡 Testado {tf_a}/{tf_e}: PF {stats['Profit Factor']:.2f}")
            
        except Exception: continue

    df_res = pd.DataFrame(resultados).sort_values(by='Retorno [%]', ascending=False)
    print("\n🏆 RANKING DE EFICIÊNCIA HARMÔNICA (ETH):")
    print(df_res.to_string(index=False))

if __name__ == "__main__":
    rodar_colisor_eth()
