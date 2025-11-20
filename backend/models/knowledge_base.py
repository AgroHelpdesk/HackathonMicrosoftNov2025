"""
Knowledge Base Model - Modelo de dados para documentos da base de conhecimento
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class KnowledgeDocument(BaseModel):
    """Documento da base de conhecimento"""
    id: str
    source: str  # "MAPA", "AGROFIT", "PDF", etc.
    type: str  # "FAQ", "PRODUCT", "MANUAL", etc.
    category: str
    title: str
    content: str
    keywords: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    score: Optional[float] = None  # Relevance score from search
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "FAQ-68037",
                "source": "MAPA",
                "type": "FAQ",
                "category": "ABASTECIMENTO",
                "title": "Assuntos Relacionados a Cesta Básica",
                "content": "O MAPA não trata mais de assuntos relacionados a cesta básica...",
                "keywords": ["cesta", "básica", "abastecimento", "CONAB"],
                "metadata": {},
                "score": 0.95
            }
        }


class SearchQuery(BaseModel):
    """Query de busca na base de conhecimento"""
    query: str
    filters: dict = Field(default_factory=dict)
    top: int = 5
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "como controlar fungos na soja",
                "filters": {"source": "MAPA"},
                "top": 5
            }
        }


class SearchResult(BaseModel):
    """Resultado de busca"""
    documents: List[KnowledgeDocument]
    total_count: int
    query: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "documents": [],
                "total_count": 10,
                "query": "fungos soja"
            }
        }
