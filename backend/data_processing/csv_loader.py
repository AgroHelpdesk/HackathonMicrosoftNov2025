"""
CSV Loader - Carrega e processa arquivos CSV do dataset MAPA
"""
import pandas as pd
import os
from typing import List, Dict, Any
from pathlib import Path


class CSVLoader:
    """Carregador de arquivos CSV do dataset"""
    
    def __init__(self, dataset_path: str = None):
        """
        Inicializa o loader
        
        Args:
            dataset_path: Caminho para o diretório do dataset
        """
        if dataset_path is None:
            # Caminho padrão relativo ao projeto
            self.dataset_path = Path(__file__).parent.parent.parent / "dataset"
        else:
            self.dataset_path = Path(dataset_path)
    
    def load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Carrega a base de conhecimento do MAPA (FAQs)
        
        Returns:
            Lista de dicionários com FAQs processados
        """
        csv_path = self.dataset_path / "basedeconhecimentoMAPA.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
        
        # Carregar CSV com delimitador de ponto e vírgula
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        
        # Processar e limpar dados
        faqs = []
        for _, row in df.iterrows():
            # Pular linhas vazias
            if pd.isna(row.get('numero_faq')):
                continue
            
            faq = {
                'id': f"FAQ-{row['numero_faq']}",
                'source': 'MAPA',
                'type': 'FAQ',
                'numero_faq': str(row['numero_faq']).strip(),
                'problema': str(row.get('problema', '')).strip(),
                'solucao': str(row.get('solucao', '')).strip(),
                'categoria': str(row.get('categoria_faq', '')).strip(),
            }
            
            # Extrair categorias hierárquicas
            if faq['categoria']:
                categorias = faq['categoria'].split('::')
                faq['categoria_nivel1'] = categorias[0] if len(categorias) > 0 else ''
                faq['categoria_nivel2'] = categorias[1] if len(categorias) > 1 else ''
                faq['categoria_nivel3'] = categorias[2] if len(categorias) > 2 else ''
            
            faqs.append(faq)
        
        print(f"✓ Carregados {len(faqs)} FAQs da base de conhecimento MAPA")
        return faqs
    
    def load_agrofit_products(self) -> List[Dict[str, Any]]:
        """
        Carrega produtos fitossanitários (agrotóxicos)
        
        Returns:
            Lista de dicionários com produtos processados
        """
        csv_path = self.dataset_path / "agrofitprodutostecnicos.csv"
        
        if not csv_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")
        
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        
        products = []
        for _, row in df.iterrows():
            if pd.isna(row.get('NUMERO_REGISTRO')):
                continue
            
            product = {
                'id': f"AGROFIT-{row['NUMERO_REGISTRO']}",
                'source': 'AGROFIT',
                'type': 'PRODUTO_FITOSSANITARIO',
                'numero_registro': str(row['NUMERO_REGISTRO']).strip(),
                'produto': str(row.get('PRODUTO_TECNICO_MARCA_COMERCIAL', '')).strip(),
                'ingrediente_ativo': str(row.get('INGREDIENTE_ATIVO(GRUPO_QUIMICI)(CONCENTRACAO)', '')).strip(),
                'classe': str(row.get('CLASSE', '')).strip(),
                'titular': str(row.get('TITULAR_REGISTRO', '')).strip(),
                'empresa': str(row.get('EMPRESA_<PAIS>_TIPO', '')).strip(),
                'classificacao_toxicologica': str(row.get('CLASSIFICACAO_TOXICOLOGICA', '')).strip(),
                'classificacao_ambiental': str(row.get('CLASSIFICACAO_AMBIENTAL', '')).strip(),
            }
            
            products.append(product)
        
        print(f"✓ Carregados {len(products)} produtos fitossanitários")
        return products
    
    def load_fertilizers(self) -> List[Dict[str, Any]]:
        """
        Carrega dados de fertilizantes
        
        Returns:
            Lista de dicionários com fertilizantes processados
        """
        csv_path = self.dataset_path / "sipeagrofertilizante.csv"
        
        if not csv_path.exists():
            print(f"⚠ Arquivo não encontrado: {csv_path}")
            return []
        
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        
        fertilizers = []
        for idx, row in df.iterrows():
            # Adaptar conforme estrutura real do CSV
            fertilizer = {
                'id': f"FERT-{idx}",
                'source': 'SIPEAGRO',
                'type': 'FERTILIZANTE',
                **{k: str(v).strip() for k, v in row.items() if pd.notna(v)}
            }
            fertilizers.append(fertilizer)
        
        print(f"✓ Carregados {len(fertilizers)} fertilizantes")
        return fertilizers
    
    def load_plant_quality(self) -> List[Dict[str, Any]]:
        """
        Carrega dados de qualidade vegetal
        
        Returns:
            Lista de dicionários com dados de qualidade vegetal
        """
        csv_path = self.dataset_path / "sipeagroqualidadevegetal.csv"
        
        if not csv_path.exists():
            print(f"⚠ Arquivo não encontrado: {csv_path}")
            return []
        
        df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
        
        quality_data = []
        for idx, row in df.iterrows():
            item = {
                'id': f"QUAL-{idx}",
                'source': 'SIPEAGRO',
                'type': 'QUALIDADE_VEGETAL',
                **{k: str(v).strip() for k, v in row.items() if pd.notna(v)}
            }
            quality_data.append(item)
        
        print(f"✓ Carregados {len(quality_data)} registros de qualidade vegetal")
        return quality_data
    
    def load_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Carrega todos os datasets disponíveis
        
        Returns:
            Dicionário com todos os dados carregados
        """
        print("📂 Carregando datasets...")
        
        data = {
            'knowledge_base': self.load_knowledge_base(),
            'agrofit_products': self.load_agrofit_products(),
            'fertilizers': self.load_fertilizers(),
            'plant_quality': self.load_plant_quality(),
        }
        
        total = sum(len(v) for v in data.values())
        print(f"\n✅ Total de {total} registros carregados")
        
        return data


if __name__ == "__main__":
    # Teste do loader
    loader = CSVLoader()
    data = loader.load_all()
    
    # Mostrar estatísticas
    print("\n📊 Estatísticas:")
    for key, items in data.items():
        print(f"  {key}: {len(items)} registros")
        if items:
            print(f"    Exemplo: {list(items[0].keys())[:5]}...")
