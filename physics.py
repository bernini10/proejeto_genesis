import pandas as pd
import numpy as np

def pipeline_fisica(df):
    if df is None or df.empty:
        return df
    
    # Velocidade = Variação Percentual Direta (Ex: 0.0011 para 0.11%)
    df['velocity'] = df['close'].pct_change()
    
    # Aceleração = Diferença entre a velocidade atual e a anterior
    df['acceleration'] = df['velocity'].diff()
    
    return df.fillna(0)
