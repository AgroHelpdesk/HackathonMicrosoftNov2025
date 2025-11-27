"""Pydantic schemas for LLM responses.

This module defines Pydantic models for validating LLM responses,
replacing manual JSON validation with type-safe schemas.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AgroBrainResponse(BaseModel):
    """Schema for AgroBrain agent LLM response."""
    
    conhecimento: str = Field(..., description="Technical knowledge about the issue")
    riscos: str = Field(..., description="Identified risks")
    recomendacoes: str = Field(..., description="Recommendations")
    fontes: List[str] = Field(default_factory=list, description="Source document IDs")
    procedimento_conhecido: bool = Field(..., description="Whether procedure is documented")
    nivel_complexidade: str = Field(..., description="Complexity level: baixo, medio, alto")
    requer_especialista: bool = Field(..., description="Whether specialist is required")


class FieldSenseResponse(BaseModel):
    """Schema for FieldSense agent LLM response."""
    
    intencao: str = Field(..., description="Main user intention")
    categoria: str = Field(..., description="Message category")
    entidades: dict = Field(default_factory=dict, description="Extracted entities")
    confianca: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    severidade: str = Field(..., description="Severity level: baixa, media, alta")
    observacoes: Optional[str] = Field(None, description="Additional observations")
    perguntas_sugeridas: Optional[List[str]] = Field(None, description="Suggested clarification questions")


class ExplainItResponse(BaseModel):
    """Schema for ExplainIt agent LLM response."""
    
    simplified_summary: str = Field(..., description="User-friendly explanation")
