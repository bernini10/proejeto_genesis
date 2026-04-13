import os
import sys
import time
import threading
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv
import ccxt
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich import box

# --- CONEXÃO COM A FÍSICA OFICIAL ---
sys.path.insert(0, os.getcwd())
try:
    import physics
    from physics import pipeline_fisica
    PHYS_TAG = "[bold green]OFICIAL[/bold green]"
    PHYSICS_LOADED = True
except Exception as e:
    PHYS_TAG = f"[bold red]ERRO: {str(e)[:15]}[/bold red]"
    PHYSICS_LOADED = False

load_dotenv()

SYMBOLS = ["BTC/USDT:USDT", "ETH/USDT:USDT"]
TRAVAS_ATIVAS = {s: False for s in SYMBOLS}
CONFIG_ATIVOS = {
    "BTC/USDT:USDT": {"sigma": 0.005, "tag": "BTC"},
    "ETH/USDT:USDT": {"sigma": 0.0002, "tag": "ETH"}
}

exchange = ccxt.bitget({
    "apiKey": os.getenv("BITGET_API_KEY"),
    "secret": os.getenv("BITGET_API_SECRET"),
    "password": os.getenv("BITGET_PASSPHRASE"),
    "options": {"defaultType": "swap"},
})

# Estrutura de dados simples para a carteira
def executar_ordem(symbol, lado, preco_atual):
    global TRAVAS_ATIVAS

    if TRAVAS_ATIVAS[symbol]: return "TRAVA ATIVA"
    # Dupla checagem real
    pos_check = exchange.fetch_positions([symbol])
    if any(float(p.get("size", 0)) != 0 for p in pos_check): TRAVAS_ATIVAS[symbol] = True; return "Já posicionado (API)"
    TRAVAS_ATIVAS[symbol] = True # Bloqueia imediatamente

    try:
        # Configura Alavancagem antes de operar
        exchange.set_leverage(5, symbol)
        
        # Busca saldo e regras do mercado
        bal = exchange.fetch_balance()["USDT"]["free"]
        mercado = exchange.market(symbol)
        precision = mercado["precision"]["amount"]
        min_amount = mercado["limits"]["amount"]["min"]
        
        # Cálculo de Tamanho: 95% do saldo com alavancagem 10x
        # Fórmula: (Saldo * Alavancagem) / Preço
        quantidade_bruta = (float(bal) * 0.40 * 5) / float(preco_atual)
        
        # Arredondamento Cirúrgico conforme a Exchange
        quantidade = float(exchange.amount_to_precision(symbol, quantidade_bruta))
        
        if quantidade < min_amount:
            return f"Saldo Insuficiente ({quantidade} < {min_amount})"
            
        # Verifica posição aberta para evitar Double-Entry
        pos = exchange.fetch_positions([symbol])
        if any(float(p.get("size", 0)) != 0 for p in pos):
            return "Já posicionado"
            
        order = exchange.create_market_order(symbol, lado, quantidade)
        return f"ORDEM EXECUTADA: {lado.upper()} {quantidade}"
    except Exception as e: TRAVAS_ATIVAS[symbol] = False; return f"ERRO: {str(e)[:20]}"

class Carteira:
    def __init__(self):
        self.saldo = 0.0
        self.margem = 0.0
        self.pnl = 0.0
        self.update = "--:--:--"

cart = Carteira()
_metricas_cache = {s: {"ok": False} for s in SYMBOLS}
_lock = threading.Lock()

def obter_metricas(symbol):
    try:
        ohlcv30 = exchange.fetch_ohlcv(symbol, "30m", limit=50)
        ohlcv5 = exchange.fetch_ohlcv(symbol, "5m", limit=50)
        df30 = pd.DataFrame(ohlcv30, columns=["ts","o","h","l","close","v"])
        df5 = pd.DataFrame(ohlcv5, columns=["ts","o","h","l","close","v"])
        vel, acel = 0.0, 0.0
        if PHYSICS_LOADED:
            res30 = pipeline_fisica(df30)
            vel = float(res30["velocity"].iloc[-1])
            res5 = pipeline_fisica(df5)
            if "acceleration" in res5.columns:
                acel = float(res5["acceleration"].iloc[-1]) if "acceleration" in res5.columns else 0.0
            else:
                v5_at = float(res5["velocity"].iloc[-1])
                v5_an = float(res5["velocity"].iloc[-2])
                acel = (v5_at - v5_an) / 300.0
        var = ((df30["close"].iloc[-1] - df30["close"].iloc[-2]) / df30["close"].iloc[-2] * 100)
        return {"preco": df30["close"].iloc[-1], "vel": vel, "acel": acel, "var": var, "ok": True}
    except: return {"ok": False}
def construir_header():
    txt = Align.center(Text.assemble(("  PROJETO GÊNESIS  ", "bold bright_cyan"), (" Executor de Alta Precisão ", "bold white"), (" | v3.0 | ", "dim cyan")))
    msg_btc = _metricas_cache.get("BTC/USDT:USDT", {}).get("status", "Aguardando sinal...")
    msg_eth = _metricas_cache.get("ETH/USDT:USDT", {}).get("status", "Aguardando sinal...")
    txt = f"BTC: {msg_btc}\nETH: {msg_eth}\n\nCarteira atualizada: {cart.update} | MODO EXECUCAO ATIVO"
    return Panel(txt, border_style="bright_cyan", padding=(0, 1))

def construir_painel_carteira():
    pnl_cor = "bright_green" if cart.pnl >= 0 else "bright_red"
    conteudo = (
        f"  [dim]Saldo Total    :[/dim] [bold white]${cart.saldo:,.2f}[/bold white] USDT      [dim]Margem em Uso :[/dim] [yellow]${cart.margem:,.2f}[/yellow] USDT\n"
        f"  [dim]PnL Aberto     :[/dim] [{pnl_cor}]{cart.pnl:+.4f} USDT[/{pnl_cor}]      "
        f"[dim]Drawdown Diario:[/dim] [green]0.00%[/green]\n"
        f"  [dim]Lucro Sessão   :[/dim] [green]+0.0000 USDT[/green]      [dim]Último Update :[/dim] [white]{cart.update}[/white]"
    )
    return Panel(conteudo, title="[bold green]CARTEIRA GÊNESIS[/bold green]", border_style="green")

def construir_tabela_ativos(ts):
    table = Table(title=f"[bold cyan]PROJETO GÊNESIS[/bold cyan] [dim]|[/dim] [white]Monitor Live {ts}[/white]", 
                  box=box.DOUBLE_EDGE, expand=True, border_style="cyan", header_style="bold white on dark_blue", show_lines=True,
                  caption=f"[dim]Âncora: 30m | Execução: 5m | Alavancagem: 10x | Physics: {PHYS_TAG}[/dim]")
    
    for col in ["Ativo", "Preço Atual", "Veloc. 30m", "Acel. 5m", "Sigma Alvo", "Posição", "Entrada / Erro", "Status"]:
        table.add_column(col, justify="center")

    with _lock:
        for s in SYMBOLS:
            m = _metricas_cache[s]
            sig = CONFIG_ATIVOS[s]["sigma"]
            if not m.get("ok"):
                table.add_row(CONFIG_ATIVOS[s]["tag"], "N/A", "--", "--", "--", "--", "--", "[yellow]SYNC...")
                continue
            
            st = "[bold white on red]IGNICAO SHORT" if abs(m["vel"]) > sig else "[dim]AGUARDANDO"
            preco_txt = Text.assemble((f"${m['preco']:,.2f} ", "bold"), (f"({m['var']:+.2f}%)", "green" if m['var'] >= 0 else "red"))
            table.add_row(CONFIG_ATIVOS[s]["tag"], preco_txt, f"{m['vel']:+.8f}", f"{m['acel']:+.8f}", str(sig), "--", "--", st)
    return table

def construir_log_sinais():


    msg_btc = _metricas_cache.get("BTC/USDT:USDT", {}).get("status", "Aguardando sinal...")
    msg_eth = _metricas_cache.get("ETH/USDT:USDT", {}).get("status", "Aguardando sinal...")
    txt = f"BTC: {msg_btc}\nETH: {msg_eth}\n\nCarteira atualizada: {cart.update} | MODO EXECUCAO ATIVO"
    return Panel(txt, title="[bold]Log de Sinais[/bold]", border_style="dim cyan", padding=(0, 2))

def renderizar():
    ts = datetime.now().strftime("%H:%M:%S")
    l = Layout()
    l.split_column(Layout(construir_header(), size=3), Layout(construir_painel_carteira(), size=7), Layout(construir_tabela_ativos(ts), ratio=3), Layout(construir_log_sinais(), size=7))
    return l

def worker(sym):
    while True:
        time.sleep(0.5)
        res = obter_metricas(sym)
        with _lock: _metricas_cache[sym] = res
        if res.get("ok") and abs(res["vel"]) > CONFIG_ATIVOS[sym]["sigma"]:
            lado = "buy" if res["vel"] > 0 else "sell"
            res["status"] = f"IGNICAO {lado.upper()}"
            status_exec = executar_ordem(sym, lado, res["preco"])
            print(f"--- {sym} --- {status_exec}")
        time.sleep(10)

if __name__ == "__main__":
    for s in SYMBOLS: threading.Thread(target=worker, args=(s,), daemon=True).start()
    with Live(renderizar(), refresh_per_second=1, screen=True) as live:
        while True:
            try:
                bal = exchange.fetch_balance({"type": "swap"})['USDT']
                pos = exchange.fetch_positions(SYMBOLS)
                pnl = sum(float(p.get("unrealizedPnl", 0)) for p in pos)
                cart.saldo, cart.margem, cart.pnl = float(bal['total']), float(bal['used']), pnl
                cart.update = datetime.now().strftime("%H:%M:%S")
                live.update(renderizar())
            except: pass
            time.sleep(1)