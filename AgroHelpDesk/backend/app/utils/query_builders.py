"""Centralized query builders for agents.

This module provides reusable functions to build search queries
and enhanced user queries from context data.
"""

from typing import Any, Dict, List


def build_search_query_from_context(
    message: str,
    fieldsense_data: Dict[str, Any],
    farmops_data: Dict[str, Any]
) -> str:
    """Build search query from available context data.
    
    Extracts relevant terms from FieldSense and FarmOps data to create
    an optimized search query for AI Search.
    
    Args:
        message: Original user message
        fieldsense_data: Data from FieldSense agent
        farmops_data: Data from FarmOps agent
        
    Returns:
        Search query string optimized for AI Search
    """
    query_parts = []
    
    # Add category from FieldSense
    categoria = fieldsense_data.get("categoria")
    if categoria and categoria != "outro":
        query_parts.append(categoria.replace("_", " "))
    
    # Add entities from FieldSense
    entidades = fieldsense_data.get("entidades", {})
    
    if entidades.get("maquina"):
        query_parts.append(entidades["maquina"])
    
    if entidades.get("sintomas"):
        query_parts.append(entidades["sintomas"])
    
    if entidades.get("praga"):
        query_parts.append(entidades["praga"])
    
    # Add machine model from FarmOps
    machine_data = farmops_data.get("machine_data", {})
    if machine_data and machine_data.get("modelo"):
        query_parts.append(machine_data["modelo"])
    
    # Add telemetry errors from FarmOps
    telemetry = farmops_data.get("telemetry", {})
    if telemetry and telemetry.get("erros"):
        for erro in telemetry["erros"]:
            query_parts.append(f"erro {erro}")
    
    # If no specific data, use original message
    if not query_parts:
        return message
    
    return " ".join(query_parts)


def build_enhanced_user_query(
    message: str,
    fieldsense_data: Dict[str, Any],
    farmops_data: Dict[str, Any],
    additional_instructions: str = ""
) -> str:
    """Build enhanced user query with context for LLM.
    
    Combines the original message with extracted context from agents
    to provide richer information to the LLM.
    
    Args:
        message: Original user message
        fieldsense_data: Data from FieldSense agent
        farmops_data: Data from FarmOps agent
        additional_instructions: Additional instructions to append
        
    Returns:
        Enhanced query string with context
    """
    query_parts = [f"Mensagem do usuário: {message}\n"]
    
    # Add FieldSense interpretation
    if fieldsense_data:
        intencao = fieldsense_data.get("intencao")
        categoria = fieldsense_data.get("categoria")
        
        if intencao:
            query_parts.append(f"Intenção identificada: {intencao}")
        if categoria:
            query_parts.append(f"Categoria: {categoria}")
    
    # Add FarmOps operational data
    if farmops_data:
        machine_id = farmops_data.get("machine_id")
        telemetry = farmops_data.get("telemetry", {})
        
        if machine_id:
            query_parts.append(f"Máquina: {machine_id}")
        
        if telemetry and telemetry.get("temp_motor"):
            query_parts.append(f"Temperatura do motor: {telemetry['temp_motor']}°C")
        
        if telemetry and telemetry.get("erros"):
            query_parts.append(f"Erros detectados: {', '.join(telemetry['erros'])}")
    
    # Add additional instructions if provided
    if additional_instructions:
        query_parts.append(f"\n{additional_instructions}")
    
    return "\n".join(query_parts)


def extract_context_summary(
    fieldsense_data: Dict[str, Any],
    agrobrain_data: Dict[str, Any],
    work_order: Any = None,
    runbook_execution: Any = None,
    max_knowledge_length: int = 200
) -> List[str]:
    """Extract summary parts from context for explanation generation.
    
    Args:
        fieldsense_data: Data from FieldSense agent
        agrobrain_data: Data from AgroBrain agent
        work_order: Work order if created
        runbook_execution: Runbook execution result if executed
        max_knowledge_length: Maximum length of knowledge text to include
        
    Returns:
        List of summary parts to be joined
    """
    summary_parts = []
    
    # Add FieldSense data
    if fieldsense_data:
        intencao = fieldsense_data.get("intencao", "")
        categoria = fieldsense_data.get("categoria", "")
        if intencao:
            summary_parts.append(f"Problema identificado: {intencao}")
        if categoria:
            summary_parts.append(f"Categoria: {categoria}")
    
    # Add AgroBrain data
    if agrobrain_data:
        conhecimento = agrobrain_data.get("conhecimento", "")
        if conhecimento:
            # Limit to first N chars
            summary_parts.append(f"Análise técnica: {conhecimento[:max_knowledge_length]}")
        riscos = agrobrain_data.get("riscos")
        if riscos:
            summary_parts.append(f"Riscos: {riscos}")
    
    # Add action taken
    if work_order:
        summary_parts.append(
            f"\nAção: Ordem de serviço criada (ID: {work_order.get('order_id')})"
        )
        summary_parts.append(f"Especialista: {work_order.get('assigned_specialist')}")
        summary_parts.append(f"Prioridade: {work_order.get('priority')}")
    elif runbook_execution:
        if runbook_execution.get("success"):
            summary_parts.append(
                f"\nAção: Procedimento '{runbook_execution.get('runbook_name')}' executado com sucesso"
            )
        else:
            summary_parts.append(
                f"\nAção: Tentativa de executar '{runbook_execution.get('runbook_name')}' falhou"
            )
    else:
        summary_parts.append("\nAção: Encaminhado para análise especializada")
    
    return summary_parts
