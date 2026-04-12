from pydantic import BaseModel, Field
import instructor
from openai import OpenAI
import os

class TradingSpec(BaseModel):
    asset: str = Field(description='Ativo analisado')
    timeframe: str = Field(description='Timeframe principal')
    entry_logic: str = Field(description='Logica de entrada baseada em velocidade/inercia')
    exit_logic: str = Field(description='Logica de saida')
    risk_pct: float = Field(ge=0.1, le=5.0)
    pine_webhook_format: str = Field(description='JSON esperado do webhook')

def generate_spec(thesis):
    client = instructor.from_openai(
        OpenAI(base_url=f"{os.getenv('OLLAMA_HOST', 'http://localhost:11434')}/v1", api_key="ollama"),
        mode=instructor.Mode.JSON
    )
    return client.chat.completions.create(
        model='qwen2.5:7b',
        response_model=TradingSpec,
        messages=[{'role': 'user', 'content': f'Transforme a tese em spec estruturada:\n{thesis}'}]
    )
