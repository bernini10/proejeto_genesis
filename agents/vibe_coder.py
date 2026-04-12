import instructor
from openai import OpenAI
import os

def generate_code(spec):
    client = OpenAI(
        base_url=f"{os.getenv('OLLAMA_HOST', 'http://localhost:11434')}/v1", 
        api_key="ollama"
    )
    
    prompt = f"""
Gere um script Python de backtest usando VECTORBT.

ESPECIFICAÇÃO:
{spec}

REGRAS DE OURO (NÃO DESVIE):
1. Importe: from core.physics import pipeline_fisica
2. Carregue: data/ohlcv/BTC_USDT_1h.parquet
3. Pipeline: df = pipeline_fisica(df)
4. SINAIS: Crie 'entries' e 'exits' como Séries booleanas do Pandas diretamente das colunas do df.
   Exemplo: entries = (df['velocity'] > 0.5) & (df['inertia'] >= 4)
5. BACKTEST: Use 'vbt.Portfolio.from_signals(df.close, entries, exits, fees=0.001, freq="1H")'.
6. RETORNO: Retorne APENAS o código Python puro. Sem explicações ou métodos inexistentes como 'EventArray'.
"""
    
    response = client.chat.completions.create(
        model='qwen2.5-coder:7b',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.1
    )
    
    code = response.choices[0].message.content
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]
        
    return code.strip()
