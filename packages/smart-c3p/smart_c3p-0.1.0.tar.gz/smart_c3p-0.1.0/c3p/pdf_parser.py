import fitz  # PyMuPDF
import os
from .utils import sanitize_text

def extract_text_from_pdf(pdf_path):
    """Extrai texto de um arquivo PDF usando PyMuPDF.
    
    Args:
        pdf_path (str): Caminho para o arquivo PDF
        
    Returns:
        str: Texto extraído do PDF
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"O arquivo PDF não foi encontrado: {pdf_path}")
        
    try:
        text = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        
        return sanitize_text(text)
    except Exception as e:
        print(f"Erro ao extrair texto do PDF: {e}")
        return ""