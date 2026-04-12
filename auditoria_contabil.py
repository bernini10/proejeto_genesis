import pandas as pd
import vectorbt as vbt
from genesis_tita_final.tita_v6 import motor_tita as motor_btc
from genesis_tita_eth.tita_eth import motor_tita_eth as motor_eth

def auditar(nome, pf):
    # Extrair o índice de tempo do portfólio
    index = pf.wrapper.index
    total_days = (index[-1] - index[0]).days
    total_months = total_days / 30.44
    
    trades = pf.trades.count()
    
    # Médias de Frequência
    trades_por_mes = trades / total_months
    trades_por_dia = trades / total_days
    
    # Médias de Lucro (Cálculo Composto/Geométrico)
    retorno_total = pf.total_return()
    lucro_medio_mensal = ((1 + retorno_total) ** (1 / total_months) - 1) * 100
    lucro_medio_diario = ((1 + retorno_total) ** (1 / total_days) - 1) * 100

    print(f"\n--- 📈 ESTATÍSTICAS DE CONTA: {nome} ---")
    print(f"Frequência Operacional:")
    print(f"  - Trades por Mês: {trades_por_mes:.2f}")
    print(f"  - Trades por Dia: {trades_por_dia:.2f}")
    print(f"Rentabilidade Média:")
    print(f"  - Lucro Médio Mensal: {lucro_medio_mensal:.2f}%")
    print(f"  - Lucro Médio Diário: {lucro_medio_diario:.2f}%")
    print(f"  - Total de Trades: {trades}")

# Executar Auditoria
auditar("BITCOIN (Titã v6)", motor_btc())
auditar("ETHEREUM (Titã v6)", motor_eth())
