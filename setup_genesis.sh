#!/usr/bin/env bash
set -euo pipefail

echo "🚀 PROJETO GENESIS - Setup Completo (Velocímetro de Fluxo e Vetores)"
echo "==================================================================="

# 1. Cria estrutura de pastas
mkdir -p core agents data/ohlcv pine tests logs

# 2. .env.example
cat << 'EOF' > .env.example
# Chaves API (opcionais para fase R&D local)
# BINANCE_API_KEY=
# BINANCE_SECRET_KEY=
# OPENROUTER_API_KEY= # Fallback cloud (se quiser)
OLLAMA_HOST=http://localhost:11434
FASTAPI_PORT=8000
EOF

# 3. requirements.txt
cat << 'EOF' > requirements.txt
ccxt>=4.1.0
pandas>=2.1.0
numpy>=1.26.0
pyarrow>=14.0.0
langgraph>=0.2.0
langchain-ollama>=0.2.0
pydantic>=2.9.0
instructor>=1.4.0
vectorbt>=0.26.0
fastapi>=0.115.0
uvicorn>=0.30.0
pytest>=7.4.0
python-dotenv>=1.0.0
EOF

# 4. core/config.py
cat << 'EOF' > core/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "ohlcv"
LOGS_DIR = BASE_DIR / "logs"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", "8000"))

TIMEFRAMES = ["1m", "5m", "15m", "30m", "1h", "4h", "12h"]
SYMBOL = "BTC/USDT"

DEFAULT_THESIS = "Compra quando velocidade de alta supera 0.8 com inércia >= 5 candles e saldo de pressão positivo. Stop 1.5%, Take 3%."
EOF

# 5. core/physics.py
cat << 'EOF' > core/physics.py
import pandas as pd
import numpy as np

def calcular_velocidade(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    dt_seconds = (df.index[1] - df.index[0]).total_seconds()
    df['price_change'] = df['close'].diff()
    df['velocity'] = df['price_change'] / dt_seconds
    return df

def calcular_inercia(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    direction = np.sign(df['close'].diff())
    df['inertia'] = direction.groupby((direction != direction.shift()).cumsum()).cumcount() + 1
    return df

def calcular_vetor_ataque(df: pd.DataFrame, window: int) -> pd.DataFrame:
    df = df.copy()
    df['is_bull'] = df['velocity'] > 0
    df['attack_bull'] = df.loc[df['is_bull'], 'velocity'].rolling(window, min_periods=1).sum()
    df['attack_bear'] = df.loc[~df['is_bull'], 'velocity'].rolling(window, min_periods=1).sum().abs()
    df['attack_bull'] = df['attack_bull'].fillna(0)
    df['attack_bear'] = df['attack_bear'].fillna(0)
    return df

def calcular_saldo_pressao(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['pressure_balance'] = df['attack_bull'] - df['attack_bear']
    return df

def pipeline_fisica(df: pd.DataFrame) -> pd.DataFrame:
    df = calcular_velocidade(df)
    df = calcular_inercia(df)
    # Janelas em candles (ex: no 1m, 5 candles = 5m, 60 = 1h, 720 = 12h)
    for w in [5, 15, 60, 240, 720]:
        df = calcular_vetor_ataque(df, w)
    df = calcular_saldo_pressao(df)
    return df
EOF

# 6. core/theses.py
cat << 'EOF' > core/theses.py
import pandas as pd
import numpy as np

def tese_inercia_critica(df: pd.DataFrame, v_thresh: float = 0.8, min_inertia: int = 5) -> dict:
    sig = (df['velocity'].abs() > v_thresh) & (df['inertia'] >= min_inertia)
    if not sig.any(): return {"n_sinais": 0, "win_rate": 0.0}
    next_dir = np.sign(df['close'].diff().shift(-1))
    curr_dir = np.sign(df['velocity'])
    wins = (next_dir == curr_dir)[sig].sum()
    total = sig.sum()
    return {"n_sinais": int(total), "win_rate": round(wins/total, 3)}

def tese_exaustao_vetor(df: pd.DataFrame, peak_lookback: int = 10) -> dict:
    df = df.copy()
    df['vel_abs'] = df['velocity'].abs()
    df['is_peak'] = df['vel_abs'] == df['vel_abs'].rolling(peak_lookback).max()
    df['decel'] = df['velocity'].diff() < 0
    df['opp_acc'] = -df['velocity'].diff().shift(1) > 0
    sig = df['is_peak'] & df['decel'] & df['opp_acc']
    if not sig.any(): return {"n_sinais": 0, "reversal_rate": 0.0}
    next_rev = (np.sign(df['close'].diff().shift(-1)) != np.sign(df['velocity'].shift(-1)))[sig].sum()
    return {"n_sinais": int(sig.sum()), "reversal_rate": round(next_rev/sig.sum(), 3)}

def tese_dominio_fluxo(df: pd.DataFrame, squeeze_lookback: int = 20) -> dict:
    df = df.copy()
    df['pressure_extreme'] = df['pressure_balance'].abs() > df['pressure_balance'].rolling(squeeze_lookback).std() * 2
    df['vol_surge'] = df['volume'] > df['volume'].rolling(squeeze_lookback).mean() * 1.5
    df['range_break'] = (df['close'] - df['close'].shift(squeeze_lookback)).abs() > df['close'].rolling(squeeze_lookback).std() * 1.5
    sig = df['pressure_extreme'].shift(1)
    wins = (df['vol_surge'] & df['range_break'])[sig].sum()
    total = sig.sum()
    return {"n_sinais": int(total), "squeeze_accuracy": round(wins/total, 3) if total > 0 else 0.0}
EOF

# 7. agents/sdd_spec.py
cat << 'EOF' > agents/sdd_spec.py
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
import instructor
import os

class TradingSpec(BaseModel):
    asset: str = Field(description="Ativo analisado")
    timeframe: str = Field(description="Timeframe principal (ex: 15m)")
    entry_logic: str = Field(description="Lógica de entrada baseada em velocidade/inércia")
    exit_logic: str = Field(description="Lógica de saída (stop/take/reversão)")
    risk_pct: float = Field(ge=0.1, le=5.0, description="Risco por operação %")
    pine_webhook_format: str = Field(description="JSON esperado do webhook Pine")

def generate_spec(thesis: str) -> TradingSpec:
    client = instructor.from_llm(
        ChatOllama(model="qwen2.5:7b", temperature=0.2, base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    )
    return client.chat.completions.create(
        model="qwen2.5:7b",
        response_model=TradingSpec,
        messages=[{"role": "user", "content": f"Transforme a tese em spec estruturada para backtest:\n{thesis}"}]
    )
EOF

# 8. agents/vibe_coder.py
cat << 'EOF' > agents/vibe_coder.py
from langchain_ollama import ChatOllama
import instructor
import os

def generate_code(spec: dict) -> str:
    client = instructor.from_llm(
        ChatOllama(model="qwen2.5-coder:7b", temperature=0.1, base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
    )
    prompt = f"""
    Gere APENAS código Python válido para backtest com vectorbt, seguindo esta spec:
    {spec}
    Regras:
    - Use pandas + vectorbt
    - Funções obrigatórias: load_data(tf: str), run_backtest(), evaluate_metrics()
    - Sem explicações, só código
    - Carregue dados de data/ohlcv/
    """
    response = client.chat.completions.create(
        model="qwen2.5-coder:7b",
        response_model=str,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.strip("```python").strip("```")
EOF

# 9. agents/validator.py
cat << 'EOF' > agents/validator.py
import subprocess, sys
from pathlib import Path

def run_tests() -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True, text=True
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout,
        "stderr": result.stderr
    }
EOF

# 10. agents/graph.py
cat << 'EOF' > agents/graph.py
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from .sdd_spec import generate_spec
from .vibe_coder import generate_code
from .validator import run_tests
import json

class RnDState(TypedDict):
    thesis: str
    spec: Optional[dict]
    code: Optional[str]
    test_result: Optional[dict]
    status: str

def sdd_node(state: RnDState) -> RnDState:
    spec = generate_spec(state["thesis"])
    state["spec"] = spec.model_dump()
    state["status"] = "spec_ready"
    return state

def vibe_node(state: RnDState) -> RnDState:
    code = generate_code(json.dumps(state["spec"], indent=2))
    Path("generated_strategy.py").write_text(code)
    state["code"] = code
    state["status"] = "coded"
    return state

def validate_node(state: RnDState) -> RnDState:
    state["test_result"] = run_tests()
    state["status"] = "validated" if state["test_result"]["success"] else "failed"
    return state

def build_graph():
    workflow = StateGraph(RnDState)
    workflow.add_node("sdd", sdd_node)
    workflow.add_node("vibe", vibe_node)
    workflow.add_node("validate", validate_node)
    workflow.set_entry_point("sdd")
    workflow.add_edge("sdd", "vibe")
    workflow.add_edge("vibe", "validate")
    workflow.add_edge("validate", END)
    return workflow.compile()
EOF

# 11. data/fetch_btc.py
cat << 'EOF' > data/fetch_btc.py
import ccxt, pandas as pd, os, time
from pathlib import Path

EXCHANGE = "binance"
SYMBOL = "BTC/USDT"
TIMEFRAMES = ["1m","5m","15m","30m","1h","4h","12h"]
DATA_DIR = Path("data/ohlcv")
DATA_DIR.mkdir(parents=True, exist_ok=True)

exchange = ccxt.binance({"enableRateLimit": True})

for tf in TIMEFRAMES:
    file = DATA_DIR / f"{SYMBOL.replace('/', '_')}_{tf}.parquet"
    if file.exists():
        print(f"✅ {tf} já existe")
        continue

    print(f"📥 Baixando {tf}...")
    since = exchange.parse8601("2020-01-01T00:00:00Z")
    all_candles = []
    while True:
        ohlcv = exchange.fetch_ohlcv(SYMBOL, tf, since=since, limit=1000)
        if not ohlcv: break
        all_candles.extend(ohlcv)
        since = ohlcv[-1][0] + 1
        time.sleep(0.3)

    df = pd.DataFrame(all_candles, columns=["timestamp","open","high","low","close","volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    df.to_parquet(file, engine="pyarrow")
    print(f"💾 Salvo {file} ({len(df)} candles)")
EOF

# 12. pine/velocimetro_sensor.pine
cat << 'EOF' > pine/velocimetro_sensor.pine
//@version=5
indicator("Velocímetro de Fluxo e Vetores", overlay=false, precision=4)

len_velocity = input.int(14, "Janela Velocidade")
len_inertia  = input.int(5,  "Inércia Mínima")
len_pressure = input.int(20, "Saldo de Pressão (candles)")

dt = timeframe.in_seconds
vel = (close - close[1]) / dt
dir = ta.sgn(vel)

inertia = 0.0
for i = 1 to len_inertia
    if dir == dir[i]
        inertia += 1
    else
        break

bull_vec = 0.0, bear_vec = 0.0
for i = 0 to len_velocity - 1
    v = vel[i]
    if v > 0 then bull_vec += v
    else bear_vec += math.abs(v)

pressure = bull_vec - bear_vec

plot(vel, "Velocidade", color=vel >= 0 ? color.green : color.red, linewidth=2)
plot(bull_vec, "Vetor Alta", color=color.green, transp=50)
plot(bear_vec, "Vetor Baixa", color=color.red, transp=50)
plot(pressure, "Saldo de Pressão", color=pressure >= 0 ? color.blue : color.purple, linewidth=3)

cond_inertia = inertia >= len_inertia and math.abs(vel) > ta.avg(ta.abs(vel), len_velocity) * 1.5
alertcondition(cond_inertia, "Inercia_Critica", '{"tese":"inercia","dir":"' + (vel>0?"long":"short") + '"}')

cond_exaustao = vel > 0 and vel < vel[1] and -vel[1] > 0
alertcondition(cond_exaustao, "Exaustao_Vetor", '{"tese":"exaustao","dir":"short"}')

cond_pressao = math.abs(pressure) > ta.stdev(pressure, len_pressure) * 2
alertcondition(cond_pressao, "Dominio_Fluxo", '{"tese":"dominio","saldo":"' + str.tostring(pressure) + '"}')
EOF

# 13. tests/test_physics_and_theses.py
cat << 'EOF' > tests/test_physics_and_theses.py
import pandas as pd
import numpy as np
from core.physics import pipeline_fisica
from core.theses import tese_inercia_critica, tese_exaustao_vetor, tese_dominio_fluxo
from pathlib import Path
import pytest

def load_test_data():
    f = Path("data/ohlcv/BTC_USDT_15m.parquet")
    if not f.exists():
        pytest.skip("Dados não baixados. Rode python data/fetch_btc.py primeiro.")
    return pd.read_parquet(f)

def test_physics_pipeline():
    df = load_test_data()
    out = pipeline_fisica(df)
    assert "velocity" in out.columns
    assert "inertia" in out.columns
    assert "pressure_balance" in out.columns
    assert len(out) == len(df)

def test_theses_execution():
    df = load_test_data()
    df = pipeline_fisica(df)
    res1 = tese_inercia_critica(df)
    res2 = tese_exaustao_vetor(df)
    res3 = tese_dominio_fluxo(df)
    assert "n_sinais" in res1
    assert "win_rate" in res1
    assert "reversal_rate" in res2
    assert "squeeze_accuracy" in res3
EOF

# 14. main.py
cat << 'EOF' > main.py
from fastapi import FastAPI, Request
import logging, json
from datetime import datetime
import uvicorn
from core.config import FASTAPI_PORT

app = FastAPI(title="Projeto Genesis - Velocímetro de Fluxo")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger("genesis")

@app.post("/webhook/pine")
async def receive_pine_alert(request: Request):
    payload = await request.json()
    log.info(f"📡 Pine Sensor: {json.dumps(payload)}")
    return {"status": "received", "ts": datetime.utcnow().isoformat(), "payload": payload}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "genesis-webhook"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=FASTAPI_PORT, reload=False)
EOF

# 15. run_pipeline.py
cat << 'EOF' > run_pipeline.py
import sys, json
from agents.graph import build_graph
from core.config import DEFAULT_THESIS

def main():
    thesis = DEFAULT_THESIS if len(sys.argv) < 2 else " ".join(sys.argv[1:])
    print(f"🔬 Iniciando R&D para: {thesis}")
    app = build_graph()
    result = app.invoke({"thesis": thesis, "status": "start"})
    print("\n📊 RESULTADO DA VALIDAÇÃO:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
EOF

# 16. README.md
cat << 'EOF' > README.md
# 🌊 Projeto Genesis: Velocímetro de Fluxo e Vetores
Laboratório de R&D para validação de teses baseadas em **Engenharia de Mercado / Mecânica de Fluxo**.  
Aborda o preço como um corpo físico sujeito a leis cinéticas: Velocidade, Inércia, Vetores de Ataque e Saldo de Pressão.

## 📐 Teses Validadas
1. **Inércia Crítica**: Movimento com velocidade X + inércia Y → probabilidade >Z% de continuação.
2. **Exaustão de Vetor**: Pico de velocidade + desaceleração + aceleração oposta → reversão iminente.
3. **Domínio de Fluxo**: Saldo de pressão extremo antecipa squeezes de liquidação.

## 🛠️ Stack
- **Python**: Cérebro, backtest, orquestração (LangGraph)
- **Pine Script v5**: Sensor visual + webhook de alertas
- **Ollama + Qwen2.5-7B**: LLM local ($0 custo)
- **VectorBT + CCXT**: Backtest + dados históricos
- **FastAPI**: Webhook receptor

## 🚀 Setup & Run
```bash
# 1. Instale dependências e baixe dados
bash setup_genesis.sh

# 2. Rode o pipeline SDD → Vibe → Validação
python run_pipeline.py "Sua tese aqui"

# 3. Inicie webhook para TradingView
python main.py
