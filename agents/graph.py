from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from .sdd_spec import generate_spec
from .vibe_coder import generate_code
from .validator import run_tests
import json
from pathlib import Path

class RnDState(TypedDict):
    thesis: str
    spec: Optional[dict]
    code: Optional[str]
    test_result: Optional[dict]
    status: str

def sdd_node(state):
    print("\n[1/3] 🧠 Agente SDD: Criando especificação técnica...")
    spec = generate_spec(state['thesis'])
    state['spec'] = spec.model_dump()
    print(f"✅ Spec gerada para: {state['spec']['asset']} ({state['spec']['timeframe']})")
    return state

def vibe_node(state):
    print("[2/3] 💻 Agente Vibe Coder: Escrevendo código de backtest...")
    code = generate_code(json.dumps(state['spec'], indent=2))
    Path('generated_strategy.py').write_text(code)
    state['code'] = code
    print("✅ Código escrito em 'generated_strategy.py'")
    return state

def validate_node(state):
    print("[3/3] 🧪 Agente Validator: Executando bateria de testes...")
    state['test_result'] = run_tests()
    state['status'] = 'validated' if state['test_result']['success'] else 'failed'
    print(f"✅ Resultado: {state['status'].upper()}")
    return state

def build_graph():
    workflow = StateGraph(RnDState)
    workflow.add_node('sdd', sdd_node)
    workflow.add_node('vibe', vibe_node)
    workflow.add_node('validate', validate_node)
    workflow.set_entry_point('sdd')
    workflow.add_edge('sdd', 'vibe')
    workflow.add_edge('vibe', 'validate')
    workflow.add_edge('validate', END)
    return workflow.compile()
