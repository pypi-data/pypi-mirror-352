def validate_dataframe(df):
    """Valida se o DataFrame está no formato esperado"""
    if df is None or df.empty:
        return False
    return True

def sanitize_text(text):
    """Limpa e prepara texto para análise"""
    if not text:
        return ""
    return text.strip()

def get_dataframe_summary(df):
    """Retorna um resumo das informações do DataFrame"""
    if not validate_dataframe(df):
        return {}
        
    summary = {
        "shape": df.shape,
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "null_counts": df.isnull().sum().to_dict(),
        "numeric_columns": list(df.select_dtypes(include=["number"]).columns),
        "categorical_columns": list(df.select_dtypes(include=["object", "category"]).columns),
        "datetime_columns": list(df.select_dtypes(include=["datetime"]).columns)
    }
    
    return summary

def detect_correlations(df, threshold=0.7):
    """Detecta correlações fortes entre colunas numéricas"""
    if not validate_dataframe(df):
        return []
        
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty or len(numeric_df.columns) < 2:
        return []
        
    corr_matrix = numeric_df.corr()
    correlations = []
    
    # Encontrar pares com correlação acima do threshold
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            col1 = corr_matrix.columns[i]
            col2 = corr_matrix.columns[j]
            corr_value = corr_matrix.iloc[i, j]
            
            if abs(corr_value) >= threshold:
                correlations.append({
                    "column1": col1,
                    "column2": col2,
                    "correlation": corr_value,
                    "type": "positiva" if corr_value > 0 else "negativa"
                })
                
    return correlations