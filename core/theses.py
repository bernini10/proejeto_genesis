import pandas as pd
import numpy as np

def tese_inercia_critica(df, v_thresh=0.8, min_inertia=5):
    sig = (df['velocity'].abs() > v_thresh) & (df['inertia'] >= min_inertia)
    sig = sig.fillna(False)
    if not sig.any(): return {'n_sinais': 0, 'win_rate': 0.0}
    next_dir = np.sign(df['close'].diff().shift(-1))
    curr_dir = np.sign(df['velocity'])
    wins = (next_dir == curr_dir)[sig].sum()
    total = sig.sum()
    return {'n_sinais': int(total), 'win_rate': round(wins/total, 3)}

def tese_exaustao_vetor(df, peak_lookback=10):
    df = df.copy()
    df['vel_abs'] = df['velocity'].abs()
    df['is_peak'] = df['vel_abs'] == df['vel_abs'].rolling(peak_lookback).max()
    df['decel'] = df['velocity'].diff() < 0
    df['opp_acc'] = -df['velocity'].diff().shift(1) > 0
    sig = (df['is_peak'] & df['decel'] & df['opp_acc']).fillna(False)
    if not sig.any(): return {'n_sinais': 0, 'reversal_rate': 0.0}
    next_rev = (np.sign(df['close'].diff().shift(-1)) != np.sign(df['velocity'].shift(-1)))[sig].sum()
    return {'n_sinais': int(sig.sum()), 'reversal_rate': round(next_rev/sig.sum(), 3)}

def tese_dominio_fluxo(df, squeeze_lookback=20):
    df = df.copy()
    df['pressure_extreme'] = df['pressure_balance'].abs() > df['pressure_balance'].rolling(squeeze_lookback).std() * 2
    df['vol_surge'] = df['volume'] > df['volume'].rolling(squeeze_lookback).mean() * 1.5
    df['range_break'] = (df['close'] - df['close'].shift(squeeze_lookback)).abs() > df['close'].rolling(squeeze_lookback).std() * 1.5
    
    # Mascara booleana limpa
    sig = df['pressure_extreme'].shift(1).fillna(False).astype(bool)
    # Alvo limpo
    target = (df['vol_surge'] & df['range_break']).fillna(False).astype(bool)
    
    wins = target[sig].sum()
    total = sig.sum()
    return {'n_sinais': int(total), 'squeeze_accuracy': round(wins/total, 3) if total > 0 else 0.0}
