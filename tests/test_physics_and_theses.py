import pandas as pd
import numpy as np
from core.physics import pipeline_fisica
from core.theses import tese_inercia_critica, tese_exaustao_vetor, tese_dominio_fluxo
from pathlib import Path
import pytest

def load_test_data():
    f = Path('data/ohlcv/BTC_USDT_15m.parquet')
    if not f.exists():
        pytest.skip('Dados nao baixados. Rode python data/fetch_btc.py primeiro.')
    return pd.read_parquet(f)

def test_physics_pipeline():
    df = load_test_data()
    out = pipeline_fisica(df)
    assert 'velocity' in out.columns
    assert 'inertia' in out.columns
    assert 'pressure_balance' in out.columns
    assert len(out) == len(df)

def test_theses_execution():
    df = load_test_data()
    df = pipeline_fisica(df)
    assert 'n_sinais' in tese_inercia_critica(df)
    assert 'reversal_rate' in tese_exaustao_vetor(df)
    assert 'squeeze_accuracy' in tese_dominio_fluxo(df)
