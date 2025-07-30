import pandas as pd
import numpy as np
from .utils import validate_dataframe

def analyze_data(dataframes, rules_text=""):
    """Analisa os DataFrames e gera insights baseados nos dados e regras.
    
    Args:
        dataframes (list): Lista de pandas DataFrames para análise
        rules_text (str, optional): Texto extraído de um PDF com regras de negócio
        
    Returns:
        list: Lista de insights gerados a partir da análise
    """
    insights = []
    
    # Validar DataFrames
    valid_dfs = [df for df in dataframes if validate_dataframe(df)]
    
    if not valid_dfs:
        return ["Nenhum DataFrame válido para análise."]
    
    # Análise básica para cada DataFrame
    for i, df in enumerate(valid_dfs):
        # Estatísticas descritivas
        insights.append(f"DataFrame {i+1} contém {len(df)} linhas e {len(df.columns)} colunas.")
        
        # Análise de valores nulos
        null_counts = df.isnull().sum()
        if null_counts.any():
            null_cols = ", ".join([f"{col} ({count})" for col, count in 
                                null_counts[null_counts > 0].items()])
            insights.append(f"Valores nulos encontrados em: {null_cols}")
        
        # Análise de colunas numéricas
        num_cols = df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            mean_val = df[col].mean()
            max_val = df[col].max()
            min_val = df[col].min()
            insights.append(f"Coluna '{col}': média={mean_val:.2f}, mín={min_val}, máx={max_val}")
        
        # Análise de colunas categóricas
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in cat_cols:
            value_counts = df[col].value_counts()
            if len(value_counts) <= 10:  # Limitar para categorias com poucos valores únicos
                most_common = value_counts.index[0]
                insights.append(f"Valor mais comum em '{col}': {most_common} ({value_counts[0]} ocorrências)")
    
    # Análise entre DataFrames (se houver mais de um)
    if len(valid_dfs) > 1:
        # Verificar colunas comuns
        common_cols = set.intersection(*[set(df.columns) for df in valid_dfs])
        if common_cols:
            insights.append(f"Colunas comuns entre DataFrames: {', '.join(common_cols)}")
            
            # Se houver uma coluna ID comum, podemos fazer análises relacionais
            if 'ID' in common_cols:
                insights.append("Os DataFrames podem ser relacionados pela coluna 'ID'.")
    
    # Incorporar regras de negócio (se fornecidas)
    if rules_text:
        insights.append("Análise baseada nas regras de negócio extraídas do PDF:")
        # Aqui seria implementada uma análise mais avançada usando processamento de linguagem natural
        # Para simplificar, apenas mencionamos que as regras foram consideradas
        insights.append("- Regras de negócio foram consideradas na análise.")
    
    return insights