"""
Indexer - Indexa dados no ChromaDB (Local RAG)
"""
import os
from typing import List, Dict, Any
from csv_loader import CSVLoader
from pdf_processor import PDFProcessor
from local_rag import LocalRAG


class LocalSearchIndexer:
    """Indexador de dados no ChromaDB Local"""
    
    def __init__(self):
        """
        Inicializa o indexador
        """
        self.rag = LocalRAG()
    
    def prepare_documents_for_indexing(self, data: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Prepara documentos para indexação
        
        Args:
            data: Dados carregados dos CSVs e PDFs
            
        Returns:
            Lista de documentos formatados para o ChromaDB
        """
        documents = []
        
        # Processar FAQs
        for faq in data.get('knowledge_base', []):
            doc = {
                'id': str(faq['id']),
                'source': str(faq['source']),
                'type': str(faq['type']),
                'category': faq.get('category', 'Geral'),
                'title': faq.get('question', '')[:500],
                'content': f"PERGUNTA: {faq.get('question', '')}\nRESPOSTA: {faq.get('answer', '')}",
                'keywords': ", ".join(faq.get('keywords', [])),
                'original_metadata': str(faq)
            }
            documents.append(doc)
        
        # Processar produtos
        for product in data.get('products', []):
            doc = {
                'id': str(product['id']),
                'source': str(product['source']),
                'type': str(product['type']),
                'category': product.get('product_class', 'Produto'),
                'title': product.get('commercial_name', '')[:500],
                'content': f"PRODUTO: {product.get('commercial_name', '')}\nINGREDIENTE ATIVO: {product.get('active_ingredient', '')}\nCLASSE: {product.get('product_class', '')}\nTOXICIDADE: {product.get('toxicological_class', '')}",
                'keywords': f"{product.get('product_class', '')}, {product.get('toxicological_class', '')}",
                'original_metadata': str(product)
            }
            documents.append(doc)
        
        # Processar PDFs
        for pdf in data.get('pdfs', []):
            doc = {
                'id': str(pdf['id']),
                'source': str(pdf['source']),
                'type': str(pdf['type']),
                'category': pdf.get('type', 'Manual'),
                'title': pdf.get('title', '')[:500],
                'content': pdf.get('content', '')[:20000],  # Limitar tamanho para embeddings locais se necessário
                'keywords': "",
                'original_metadata': str(pdf)
            }
            documents.append(doc)
        
        print(f"📦 Preparados {len(documents)} documentos para indexação")
        return documents
    
    def index_all_data(self):
        """Pipeline completo de indexação"""
        print("🚀 Iniciando indexação local completa...\n")
        
        # 1. Limpar coleção existente (opcional, mas bom para garantir consistência)
        # self.rag.delete_collection() 
        # Comentado para evitar deletar se não quiser, mas para re-indexação full é recomendado:
        try:
            self.rag.delete_collection()
        except Exception as e:
            print(f"⚠️ Aviso ao limpar coleção: {e}")

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
        
        # 5. Indexar
        print("\n⬆️  Indexando no ChromaDB...")
        self.rag.add_documents(documents)
        
        print("\n✅ Indexação concluída com sucesso!")
        print(f"📊 Total de documentos indexados: {len(documents)}")


def main():
    """Função principal"""
    # Executar indexação
    indexer = LocalSearchIndexer()
    indexer.index_all_data()


if __name__ == "__main__":
    main()
