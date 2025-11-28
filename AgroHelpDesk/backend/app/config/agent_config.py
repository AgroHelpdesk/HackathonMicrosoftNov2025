"""Agent configuration constants.

This module centralizes static configurations and mappings used by agents,
reducing inline definitions and improving maintainability.
"""

from typing import Dict, Any


# Category mapping: FieldSense categories -> WorkOrder schema categories
CATEGORY_MAPPING: Dict[str, str] = {
    "falha_mecanica": "maquinario",
    "fitossanidade": "praga",
    "estoque_insumos": "insumos",
    "meteorologia": "outro",
    "sistema_ti": "outro",
    "rh_rural": "outro",
    "manutencao_preventiva": "maquinario",
    "operacao_maquina": "maquinario",
    "duvida_operacional": "outro",
    "cumprimento": "outro",
    "outro": "outro"
}


# Specialist assignment mapping by category
SPECIALIST_MAPPING: Dict[str, str] = {
    "falha_mecanica": "Mecânico de Máquinas Agrícolas",
    "fitossanidade": "Agrônomo Especialista",
    "sistema_ti": "Técnico de TI",
    "manutencao_preventiva": "Técnico de Manutenção",
    "outro": "Supervisor de Campo"
}


# Severity to priority mapping (valores em português para match com Pydantic enums)
SEVERITY_PRIORITY_MAPPING: Dict[str, str] = {
    "alta": "alta",
    "critica": "critica",
    "media": "media",
    "baixa": "baixa"
}


# Runbook definitions
RUNBOOK_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "reset_sistema": {
        "name": "Reset de Sistema de Máquina",
        "steps": [
            "Desligar a máquina completamente",
            "Aguardar 30 segundos",
            "Verificar conexões de sensores",
            "Religar o sistema",
            "Verificar códigos de erro"
        ],
        "estimated_time_hours": 0.25,
        "difficulty": "easy",
        "pode_automatizar": True,
        "requer_aprovacao": False
    },
    "consultar_estoque": {
        "name": "Consulta de Estoque",
        "steps": [
            "Acessar sistema de gestão",
            "Buscar item no inventário",
            "Verificar quantidade disponível",
            "Validar localização no armazém"
        ],
        "estimated_time_hours": 0.1,
        "difficulty": "easy",
        "pode_automatizar": True,
        "requer_aprovacao": False
    },
    "inspecao_basica": {
        "name": "Inspeção Básica de Máquina",
        "steps": [
            "Verificar nível de óleo",
            "Verificar nível de combustível",
            "Inspecionar correia",
            "Verificar pressão dos pneus",
            "Testar freios"
        ],
        "estimated_time_hours": 0.5,
        "difficulty": "medium",
        "pode_automatizar": False,
        "requer_aprovacao": True
    }
}


def get_specialist_for_category(categoria: str) -> str:
    """Get specialist type for a given category.
    
    Args:
        categoria: Issue category
        
    Returns:
        Specialist type string
    """
    return SPECIALIST_MAPPING.get(categoria, "Supervisor de Campo")


def map_category_to_schema(fieldsense_category: str) -> str:
    """Map FieldSense category to WorkOrder schema category.
    
    Args:
        fieldsense_category: Category from FieldSense agent
        
    Returns:
        Category compatible with WorkOrder Pydantic schema
    """
    return CATEGORY_MAPPING.get(fieldsense_category, "outro")


def get_priority_for_severity(severidade: str) -> str:
    """Get priority level for a given severity.
    
    Args:
        severidade: Severity level
        
    Returns:
        Priority level string
    """
    return SEVERITY_PRIORITY_MAPPING.get(severidade, "medium")


def get_runbook_definition(runbook_name: str) -> Dict[str, Any] | None:
    """Get runbook definition by name.
    
    Args:
        runbook_name: Name of the runbook
        
    Returns:
        Runbook definition dictionary or None if not found
    """
    return RUNBOOK_DEFINITIONS.get(runbook_name)
