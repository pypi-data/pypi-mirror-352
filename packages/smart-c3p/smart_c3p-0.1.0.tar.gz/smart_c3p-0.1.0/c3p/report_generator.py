from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
from reportlab.platypus import Image

def generate_pdf_report(dataframes, insights, output_path):
    """Gera um relatório PDF com insights e visualizações dos dados.
    
    Args:
        dataframes (list): Lista de pandas DataFrames analisados
        insights (list): Lista de insights gerados pela análise
        output_path (str): Caminho para salvar o relatório PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Título
    title_style = styles['Heading1']
    elements.append(Paragraph("Relatório de Análise de Dados", title_style))
    elements.append(Spacer(1, 0.25*inch))
    
    # Data e hora
    from datetime import datetime
    date_style = styles['Normal']
    date_style.alignment = 1  # Centralizado
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style))
    elements.append(Spacer(1, 0.5*inch))
    
    # Seção de Insights
    elements.append(Paragraph("Insights Identificados", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    for i, insight in enumerate(insights, 1):
        elements.append(Paragraph(f"{i}. {insight}", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    elements.append(Spacer(1, 0.25*inch))
    
    # Seção de Dados
    elements.append(Paragraph("Resumo dos Dados", styles['Heading2']))
    elements.append(Spacer(1, 0.1*inch))
    
    for i, df in enumerate(dataframes, 1):
        if df is None or df.empty:
            continue
            
        elements.append(Paragraph(f"DataFrame {i}", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))
        
        # Resumo estatístico
        elements.append(Paragraph("Estatísticas Descritivas:", styles['Heading4']))
        
        # Converter o resumo estatístico para uma tabela
        desc_stats = df.describe().reset_index()
        desc_stats_data = [desc_stats.columns.tolist()] + desc_stats.values.tolist()
        
        # Criar tabela com estatísticas
        table = Table(desc_stats_data, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Gerar e adicionar gráficos para colunas numéricas
        num_cols = df.select_dtypes(include=['number']).columns
        if len(num_cols) > 0:
            elements.append(Paragraph("Visualizações:", styles['Heading4']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Criar um gráfico de barras para uma coluna numérica (a primeira encontrada)
            if len(num_cols) > 0:
                col = num_cols[0]
                plt.figure(figsize=(6, 4))
                plt.bar(range(len(df)), df[col])
                plt.title(f'Gráfico de {col}')
                plt.xlabel('Índice')
                plt.ylabel(col)
                plt.tight_layout()
                
                # Salvar o gráfico em um buffer
                img_buffer = io.BytesIO()
                plt.savefig(img_buffer, format='png')
                img_buffer.seek(0)
                
                # Adicionar o gráfico ao PDF
                img = Image(img_buffer, width=5*inch, height=3*inch)
                elements.append(img)
                elements.append(Spacer(1, 0.2*inch))
                plt.close()
        
        elements.append(Spacer(1, 0.25*inch))
    
    # Construir o PDF
    try:
        doc.build(elements)
        print(f"Relatório salvo com sucesso em {output_path}")
        return True
    except Exception as e:
        print(f"Erro ao gerar o relatório PDF: {e}")
        return False