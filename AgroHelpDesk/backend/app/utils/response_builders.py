"""Centralized response builders for agents.

This module provides reusable functions to build standard responses
across all agents, reducing code duplication.
"""

from typing import Any, Dict, List


def build_insufficient_info_response(
    reason: str = "Informação insuficiente na base de conhecimento"
) -> Dict[str, Any]:
    """Build standard response when information is insufficient.
    
    Args:
        reason: Reason for insufficient information
        
    Returns:
        Dictionary with standard insufficient info response
    """
    return {
        "conhecimento": "informação insuficiente",
        "riscos": "Não foi possível avaliar riscos sem informações da base de conhecimento.",
        "recomendacoes": "Consulte um especialista técnico para análise detalhada.",
        "fontes": [],
        "procedimento_conhecido": False,
        "nivel_complexidade": "alto",
        "requer_especialista": True,
        "method": "insufficient_info",
        "reason": reason
    }


def build_error_response(error_message: str) -> Dict[str, Any]:
    """Build standard error response.
    
    Args:
        error_message: Error message to include
        
    Returns:
        Dictionary with standard error response
    """
    return {
        "conhecimento": "Erro no processamento",
        "riscos": "Sistema indisponível temporariamente.",
        "recomendacoes": "Tente novamente em alguns instantes.",
        "fontes": [],
        "procedimento_conhecido": False,
        "nivel_complexidade": "alto",
        "requer_especialista": True,
        "method": "error",
        "error": error_message
    }


def build_fallback_response(
    raw_response: str,
    max_length: int = 500
) -> Dict[str, Any]:
    """Build fallback response when JSON parsing fails.
    
    Args:
        raw_response: Raw response from LLM
        max_length: Maximum length of raw response to include
        
    Returns:
        Dictionary with fallback response
    """
    return {
        "conhecimento": raw_response[:max_length] if raw_response else "Resposta não estruturada",
        "riscos": "Não foi possível estruturar a resposta adequadamente.",
        "recomendacoes": "Revise a resposta manualmente.",
        "fontes": [],
        "procedimento_conhecido": False,
        "nivel_complexidade": "alto",
        "requer_especialista": True,
        "method": "fallback",
        "raw_response": raw_response
    }


def build_fallback_classification(message: str) -> Dict[str, Any]:
    """Build fallback classification when LLM fails.
    
    Uses simple heuristics to provide basic classification.
    
    Args:
        message: Original user message
        
    Returns:
        Dictionary with basic classification
    """
    message_lower = message.lower()
    
    categoria = "outro"
    severidade = "media"
    entidades = {}
    
    # Simple keyword-based classification
    if any(word in message_lower for word in ["quebrou", "falha", "parou", "defeito", "erro"]):
        categoria = "falha_mecanica"
        severidade = "alta"
    elif any(word in message_lower for word in ["estoque", "falta", "quantidade"]):
        categoria = "estoque_insumos"
        severidade = "media"
    elif any(word in message_lower for word in ["praga", "doenca", "fungo", "lagarta"]):
        categoria = "fitossanidade"
        severidade = "alta"
    
    return {
        "intencao": "Classificação por fallback - análise limitada",
        "categoria": categoria,
        "entidades": entidades,
        "confianca": 0.4,
        "severidade": severidade,
        "observacoes": "Classificação automática por palavras-chave (OpenAI indisponível)",
        "perguntas_sugeridas": [
            "Pode fornecer mais detalhes sobre o problema?",
            "Em qual máquina ou talhão isso está ocorrendo?",
            "Quando o problema começou?"
        ],
        "raw_message": message,
        "interpretation_method": "fallback"
    }


def build_fallback_explanation(
    intencao: str,
    work_order: Any = None,
    runbook_execution: Any = None
) -> Dict[str, Any]:
    """Build fallback explanation when LLM fails.
    
    Args:
        intencao: User intention from FieldSense
        work_order: Work order if created
        runbook_execution: Runbook execution result if executed
        
    Returns:
        Dictionary with simplified summary
    """
    if work_order:
        summary = (
            f"Identificamos {intencao}.\n\n"
            f"Criamos uma ordem de serviço e acionamos um especialista.\n\n"
            f"Você será contatado em breve com mais informações."
        )
    elif runbook_execution and runbook_execution.get("success"):
        summary = (
            f"Identificamos {intencao}.\n\n"
            f"Executamos o procedimento de correção e o problema foi resolvido.\n\n"
            f"A operação pode continuar normalmente."
        )
    else:
        summary = (
            f"Recebemos {intencao}.\n\n"
            f"Estamos analisando e tomaremos as medidas necessárias.\n\n"
            f"Aguarde retorno em breve."
        )
    
    return {"simplified_summary": summary}
