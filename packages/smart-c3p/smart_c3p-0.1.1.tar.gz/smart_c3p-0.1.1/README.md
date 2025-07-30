# C3P (SmartAnalytic)

Uma biblioteca Python para geração de relatórios analíticos com IA a partir de DataFrames e PDFs de regras de negócio. O C3P permite analisar dados estruturados, extrair informações de documentos PDF e gerar relatórios detalhados com insights e visualizações.

## Características

- **Análise de DataFrames**: Geração automática de insights a partir de dados estruturados
- **Extração de texto de PDFs**: Processamento de documentos PDF para extrair regras de negócio
- **Geração de relatórios**: Criação de relatórios PDF com insights, estatísticas e visualizações
- **Detecção de correlações**: Identificação automática de correlações entre variáveis numéricas
- **Análise entre DataFrames**: Identificação de relações entre diferentes conjuntos de dados
- **Integração com regras de negócio**: Os relatórios consideram o contexto extraído de documentos PDF para análises mais completas

## Requisitos

- Python 3.7+
- pandas
- matplotlib
- PyMuPDF (fitz)
- ReportLab
- seaborn (opcional, para visualizações aprimoradas)

## Instalação

```bash
pip install smart-c3p

## Uso Básico

```import pandas as pd
from smart_c3p import SmartAnalytic

# Criar DataFrames para análise
df1 = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5],
    'Valor': [100, 200, 150, 300, 250],
    'Categoria': ['A', 'B', 'A', 'C', 'B']
})

df2 = pd.DataFrame({
    'ID': [1, 2, 3, 4, 5],
    'Data': ['2023-01-01', '2023-01-15', '2023-02-01', '2023-02-15', '2023-03-01'],
    'Status': ['Ativo', 'Inativo', 'Ativo', 'Ativo', 'Inativo']
})

# Inicializar o analisador
analyzer = SmartAnalytic()

# Carregar os DataFrames
analyzer.load_dataframes(df1, df2, names=['Vendas', 'Clientes'])

# Carregar regras de um PDF (opcional)
analyzer.load_rules_pdf("regras_negocio.pdf")

# Executar análise e obter insights
insights = analyzer.analyze()
for i, insight in enumerate(insights, 1):
    print(f"{i}. {insight}")

# Gerar relatório PDF
analyzer.generate_report("relatorio_analise.pdf")

# Obter resumo dos DataFrames
summaries = analyzer.get_summary()
print(summaries)

# Encontrar correlações fortes (threshold = 0.7)
correlations = analyzer.find_correlations(threshold=0.7)
print(correlations)
```

## Funcionalidades Detalhadas

### Carregamento de DataFrames

O método `load_dataframes` permite carregar múltiplos DataFrames pandas para análise. Opcionalmente, você pode fornecer nomes para cada DataFrame:

```python
analyzer.load_dataframes(df1, df2, names=['Vendas', 'Clientes'])
```

### Extração de Texto de PDFs

O método `load_rules_pdf` extrai texto de documentos PDF que contêm regras de negócio ou outras informações relevantes para a análise:

```python
analyzer.load_rules_pdf("caminho/para/documento.pdf")
```

### Análise de Dados

O método `analyze` processa os DataFrames carregados e gera insights baseados em:

- Estatísticas descritivas
- Análise de valores nulos
- Distribuição de valores em colunas numéricas e categóricas
- Relações entre diferentes DataFrames
- Regras de negócio extraídas de PDFs (quando disponíveis)

```python
insights = analyzer.analyze()
```

### Geração de Relatórios

O método `generate_report` cria um relatório PDF detalhado com:

- Lista de insights gerados
- Tabelas com estatísticas descritivas
- Visualizações gráficas dos dados
- Considerações com base nas regras de negócio

```python
analyzer.generate_report("relatorio_analise.pdf")
```

### Resumo de DataFrames

O método `get_summary` retorna um dicionário com informações detalhadas sobre cada DataFrame:

```python
summaries = analyzer.get_summary()
```

### Detecção de Correlações

O método `find_correlations` identifica correlações fortes entre colunas numéricas:

```python
correlations = analyzer.find_correlations(threshold=0.7)
```

## Exemplo Completo

Veja o arquivo `examples/example_usage.py` para um exemplo completo de uso da biblioteca.

## Contribuição

Contribuições são bem-vindas! Por favor, siga os passos abaixo:

1. Faça um fork do projeto
2. Crie sua branch de feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contato

- Email: ggbriel2k22@gmail.com
- GitHub: [https://github.com/GabrielDK-vish](https://github.com/GabrielDK-vish)

---

Desenvolvido com 🐓 por Gabriel
