import pandas as pd
from .utils import validate_dataframe, get_dataframe_summary, detect_correlations

class C3P:
    def __init__(self):
        self.dataframes = []
        self.rules_text = ""
        self.dataframe_names = []
        self.insights = []
        
    def load_dataframes(self, *dfs, names=None):
        """Carrega DataFrames para análise.
        
        Args:
            *dfs: Um ou mais pandas DataFrames
            names (list, optional): Nomes para identificar cada DataFrame
        """
        valid_dfs = []
        for df in dfs:
            if validate_dataframe(df):
                valid_dfs.append(df)
            else:
                print(f"Aviso: DataFrame inválido ignorado")
                
        self.dataframes.extend(valid_dfs)
        
        # Atribuir nomes aos DataFrames
        if names and len(names) >= len(valid_dfs):
            self.dataframe_names.extend(names[:len(valid_dfs)])
        else:
            # Gerar nomes automáticos
            start_idx = len(self.dataframe_names)
            self.dataframe_names.extend([f"DataFrame_{i}" for i in range(start_idx, start_idx + len(valid_dfs))])
            
        return self

    def load_rules_pdf(self, pdf_path):
        """Carrega regras de negócio a partir de um arquivo PDF.
        
        Args:
            pdf_path (str): Caminho para o arquivo PDF com regras de negócio
        """
        from .pdf_parser import extract_text_from_pdf
        self.rules_text = extract_text_from_pdf(pdf_path)
        return self

    def analyze(self):
        """Executa a análise dos dados e regras de negócio.
        
        Returns:
            list: Lista de insights gerados pela análise
        """
        from .analyzer import analyze_data
        self.insights = analyze_data(self.dataframes, self.rules_text)
        return self.insights

    def generate_report(self, output_path):
        """Gera um relatório PDF com os resultados da análise.
        
        Args:
            output_path (str): Caminho para salvar o relatório PDF
            
        Returns:
            bool: True se o relatório foi gerado com sucesso, False caso contrário
        """
        from .report_generator import generate_pdf_report
        
        # Garantir que temos insights para incluir no relatório
        if not self.insights:
            self.analyze()
            
        return generate_pdf_report(self.dataframes, self.insights, output_path)
        
    def get_summary(self):
        """Retorna um resumo dos DataFrames carregados.
        
        Returns:
            dict: Resumo dos DataFrames
        """
        summaries = {}
        for i, df in enumerate(self.dataframes):
            name = self.dataframe_names[i] if i < len(self.dataframe_names) else f"DataFrame_{i}"
            summaries[name] = get_dataframe_summary(df)
            
        return summaries
        
    def find_correlations(self, threshold=0.7):
        """Encontra correlações fortes entre colunas numéricas nos DataFrames.
        
        Args:
            threshold (float): Valor mínimo de correlação para considerar (0-1)
            
        Returns:
            dict: Correlações encontradas por DataFrame
        """
        correlations = {}
        for i, df in enumerate(self.dataframes):
            name = self.dataframe_names[i] if i < len(self.dataframe_names) else f"DataFrame_{i}"
            correlations[name] = detect_correlations(df, threshold)
            
        return correlations