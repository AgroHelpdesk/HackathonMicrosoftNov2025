"""
Indexer - Indexa dados no Azure Cognitive Search
"""
import os
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
)
from csv_loader import CSVLoader
from pdf_processor import PDFProcessor


class AzureSearchIndexer:
    """Indexador de dados no Azure Cognitive Search"""
    
    def __init__(self, endpoint: str, key: str, index_name: str = "knowledge-base"):
        """
        Inicializa o indexador
        
        Args:
            endpoint: Endpoint do Azure Search
            key: Chave de API do Azure Search
            index_name: Nome do índice
        """
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name
        
        self.credential = AzureKeyCredential(key)
        self.index_client = SearchIndexClient(endpoint, self.credential)
        self.search_client = SearchClient(endpoint, index_name, self.credential)
    
    def create_index(self):
        """Cria o índice no Azure Search"""
        print(f"📝 Criando índice '{self.index_name}'...")
        
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="source", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="type", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
            SearchableField(name="title", type=SearchFieldDataType.String, analyzer_name="pt.lucene"),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="pt.lucene"),
            SearchableField(name="keywords", type=SearchFieldDataType.Collection(SearchFieldDataType.String)),
            SimpleField(name="metadata", type=SearchFieldDataType.String),
        ]
        
        index = SearchIndex(name=self.index_name, fields=fields)
        
        try:
            self.index_client.create_or_update_index(index)
            print(f"✅ Índice '{self.index_name}' criado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar índice: {e}")
            raise
    
    def prepare_documents_for_indexing(self, data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Prepara documentos para indexação
        
        Args:
            data: Dados carregados dos CSVs e PDFs
            
        Returns:
            Lista de documentos formatados para o Azure Search
        """
        documents = []
        
        # Processar FAQs
        for faq in data.get('knowledge_base', []):
            doc = {
                'id': faq['id'],
                'source': faq['source'],
                'type': faq['type'],
                'category': faq.get('category', 'Geral'),
                'title': faq.get('question', '')[:500],  # Limitar tamanho
                'content': f"{faq.get('question', '')} {faq.get('answer', '')}",
                'keywords': faq.get('keywords', []),
                'metadata': str(faq)
            }
            documents.append(doc)
        
        # Processar produtos
        for product in data.get('products', []):
            doc = {
                'id': product['id'],
                'source': product['source'],
                'type': product['type'],
                'category': product.get('product_class', 'Produto'),
                'title': product.get('commercial_name', '')[:500],
                'content': f"{product.get('commercial_name', '')} {product.get('active_ingredient', '')} {product.get('product_class', '')}",
                'keywords': [product.get('product_class', ''), product.get('toxicological_class', '')],
                'metadata': str(product)
            }
            documents.append(doc)
        
        # Processar PDFs
        for pdf in data.get('pdfs', []):
            doc = {
                'id': pdf['id'],
                'source': pdf['source'],
                'type': pdf['type'],
                'category': pdf.get('type', 'Manual'),
                'title': pdf.get('title', '')[:500],
                'content': pdf.get('content', '')[:10000],  # Limitar tamanho
                'keywords': [],
                'metadata': str(pdf)
            }
            documents.append(doc)
        
        print(f"📦 Preparados {len(documents)} documentos para indexação")
        return documents
    
    def upload_documents(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        """
        Faz upload dos documentos para o índice
        
        Args:
            documents: Lista de documentos
            batch_size: Tamanho do lote para upload
        """
        print(f"⬆️  Fazendo upload de {len(documents)} documentos...")
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                result = self.search_client.upload_documents(documents=batch)
                success_count = sum(1 for r in result if r.succeeded)
                print(f"  ✅ Lote {i//batch_size + 1}: {success_count}/{len(batch)} documentos indexados")
            except Exception as e:
                print(f"  ❌ Erro no lote {i//batch_size + 1}: {e}")
        
        print(f"✅ Upload concluído!")
    
    def index_all_data(self):
        """Pipeline completo de indexação"""
        print("🚀 Iniciando indexação completa...\n")
        
        # 1. Criar índice
        self.create_index()
        
        # 2. Carregar dados
        print("\n📂 Carregando dados...")
        csv_loader = CSVLoader()
        data = csv_loader.load_all()
        
        # 3. Processar PDFs
        print("\n📄 Processando PDFs...")
        pdf_processor = PDFProcessor()
        data['pdfs'] = pdf_processor.process_all_pdfs()
        
        # 4. Preparar documentos
        print("\n📝 Preparando documentos...")
        documents = self.prepare_documents_for_indexing(data)
        
        # 5. Upload
        print("\n⬆️  Fazendo upload...")
        self.upload_documents(documents)
        
        print("\n✅ Indexação concluída com sucesso!")
        print(f"📊 Total de documentos indexados: {len(documents)}")


def main():
    """Função principal"""
    # Carregar configurações do ambiente
    from dotenv import load_dotenv
    load_dotenv()
    
    endpoint = os.getenv('SEARCH_SERVICE_ENDPOINT')
    key = os.getenv('SEARCH_SERVICE_KEY')
    index_name = os.getenv('SEARCH_INDEX_NAME', 'knowledge-base')
    
    if not endpoint or not key:
        print("❌ Erro: Configure SEARCH_SERVICE_ENDPOINT e SEARCH_SERVICE_KEY no arquivo .env")
        return
    
    # Executar indexação
    indexer = AzureSearchIndexer(endpoint, key, index_name)
    indexer.index_all_data()


if __name__ == "__main__":
    main()
