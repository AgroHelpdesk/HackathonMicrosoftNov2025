"""
PDF Processor - Extrai texto de arquivos PDF do dataset
"""
import os
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2


class PDFProcessor:
    """Processador de arquivos PDF"""
    
    def __init__(self, dataset_path: str = None):
        """
        Inicializa o processador
        
        Args:
            dataset_path: Caminho para o diretório do dataset
        """
        if dataset_path is None:
            self.dataset_path = Path(__file__).parent.parent.parent / "dataset"
        else:
            self.dataset_path = Path(dataset_path)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extrai texto de um arquivo PDF
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Texto extraído do PDF
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            print(f"❌ Erro ao processar {pdf_path.name}: {e}")
            return ""
    
    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Processa um PDF e retorna documento estruturado
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Dicionário com dados do documento
        """
        text = self.extract_text_from_pdf(pdf_path)
        
        # Extrair metadados do nome do arquivo
        filename = pdf_path.stem
        
        # Identificar tipo de documento baseado no nome
        doc_type = "MANUAL"
        if "manutencao" in filename.lower():
            doc_type = "MANUAL_MANUTENCAO"
        elif "graos" in filename.lower() or "grãos" in filename.lower():
            doc_type = "MANUAL_GRAOS"
        elif "grc" in filename.lower():
            doc_type = "MANUAL_OPERACAO"
        
        document = {
            'id': f"PDF-{filename}",
            'source': 'PDF',
            'type': doc_type,
            'filename': pdf_path.name,
            'title': self._extract_title(text),
            'content': text,
            'page_count': text.count('\n\n'),  # Aproximação
            'word_count': len(text.split()),
        }
        
        return document
    
    def _extract_title(self, text: str) -> str:
        """
        Tenta extrair o título do documento
        
        Args:
            text: Texto do documento
            
        Returns:
            Título extraído ou primeira linha
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if lines:
            # Pegar primeira linha não vazia como título
            return lines[0][:100]  # Limitar a 100 caracteres
        return "Sem título"
    
    def process_all_pdfs(self) -> List[Dict[str, Any]]:
        """
        Processa todos os PDFs no diretório do dataset
        
        Returns:
            Lista de documentos processados
        """
        print("📄 Processando arquivos PDF...")
        
        pdf_files = list(self.dataset_path.glob("*.pdf"))
        documents = []
        
        for pdf_path in pdf_files:
            print(f"  Processando: {pdf_path.name}")
            doc = self.process_pdf(pdf_path)
            if doc['content']:
                documents.append(doc)
                print(f"    ✓ {doc['word_count']} palavras extraídas")
            else:
                print(f"    ⚠ Nenhum conteúdo extraído")
        
        print(f"\n✅ {len(documents)} PDFs processados com sucesso")
        return documents


# Versão alternativa usando Azure Document Intelligence (Form Recognizer)
# Descomente se tiver acesso ao serviço Azure
"""
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

class AzurePDFProcessor(PDFProcessor):
    def __init__(self, endpoint: str, key: str, dataset_path: str = None):
        super().__init__(dataset_path)
        self.client = DocumentAnalysisClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        with open(pdf_path, 'rb') as file:
            poller = self.client.begin_analyze_document(
                "prebuilt-document", document=file
            )
            result = poller.result()
            
            text = ""
            for page in result.pages:
                for line in page.lines:
                    text += line.content + "\n"
            
            return text.strip()
"""


if __name__ == "__main__":
    # Teste do processador
    processor = PDFProcessor()
    documents = processor.process_all_pdfs()
    
    # Mostrar estatísticas
    print("\n📊 Estatísticas:")
    for doc in documents:
        print(f"  {doc['filename']}")
        print(f"    Tipo: {doc['type']}")
        print(f"    Título: {doc['title']}")
        print(f"    Palavras: {doc['word_count']}")
        print()
