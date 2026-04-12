import pandas as pd
import numpy as np

def calcular_velocidade(df):
    df = df.copy()
    dt_seconds = (df.index[1] - df.index[0]).total_seconds()
    df['price_change'] = df['close'].diff()
    df['velocity'] = df['price_change'] / dt_seconds
    return df

def calcular_inercia(df):
    df = df.copy()
    direction = np.sign(df['close'].diff())
    df['inertia'] = direction.groupby((direction != direction.shift()).cumsum()).cumcount() + 1
    return df

def calcular_vetor_ataque(df, window):
    df = df.copy()
    df['is_bull'] = df['velocity'] > 0
    df['attack_bull'] = df.loc[df['is_bull'], 'velocity'].rolling(window, min_periods=1).sum()
    df['attack_bear'] = df.loc[~df['is_bull'], 'velocity'].rolling(window, min_periods=1).sum().abs()
    df['attack_bull'] = df['attack_bull'].fillna(0)
    df['attack_bear'] = df['attack_bear'].fillna(0)
    return df

def calcular_saldo_pressao(df):
    df = df.copy()
    df['pressure_balance'] = df['attack_bull'] - df['attack_bear']
    return df

def pipeline_fisica(df):
    df = calcular_velocidade(df)
    df = calcular_inercia(df)
    for w in [5, 15, 60, 240, 720]:
        df = calcular_vetor_ataque(df, w)
    return calcular_saldo_pressao(df)
