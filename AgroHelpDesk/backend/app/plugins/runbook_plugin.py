"""Runbook execution plugin for Semantic Kernel.

This plugin provides runbook execution and automation capabilities.
"""

import uuid
from datetime import datetime
from typing import Annotated, Dict, Any, List, Optional

from semantic_kernel.functions import kernel_function

from app.utils.logger import get_logger

logger = get_logger("runbook_plugin")


class RunbookPlugin:
    """Plugin for runbook execution and automation."""
    
    def __init__(self):
        """Initialize runbook plugin."""
        # In a real system, this would load from a database
        self.available_runbooks = {
            "reset_machine": {
                "name": "Reset de Máquina",
                "description": "Reinicia sistema de máquina agrícola",
                "steps": [
                    "Desligar máquina completamente",
                    "Aguardar 30 segundos",
                    "Verificar conexões elétricas",
                    "Religar máquina",
                    "Verificar painel de controle"
                ],
                "estimated_time": "5 minutos"
            },
            "clear_error_code": {
                "name": "Limpeza de Código de Erro",
                "description": "Limpa códigos de erro do sistema",
                "steps": [
                    "Acessar menu de diagnóstico",
                    "Selecionar 'Limpar Erros'",
                    "Confirmar limpeza",
                    "Reiniciar sistema"
                ],
                "estimated_time": "3 minutos"
            },
            "filter_check": {
                "name": "Verificação de Filtros",
                "description": "Procedimento de verificação de filtros",
                "steps": [
                    "Localizar filtro de ar",
                    "Verificar sujeira/obstrução",
                    "Limpar ou substituir se necessário",
                    "Verificar filtro de óleo",
                    "Registrar manutenção"
                ],
                "estimated_time": "15 minutos"
            }
        }
    
    @kernel_function(
        name="check_runbook_available",
        description="Check if a runbook is available for automation"
    )
    async def check_runbook_available(
        self,
        procedure_name: Annotated[str, "Name or description of the procedure"]
    ) -> Annotated[bool, "True if runbook is available"]:
        """Check if a runbook is available for the given procedure.
        
        Args:
            procedure_name: Name or description of the procedure
            
        Returns:
            True if runbook is available
        """
        procedure_lower = procedure_name.lower()
        
        # Check for keywords
        if any(word in procedure_lower for word in ["reset", "reiniciar", "reinício"]):
            return True
        elif any(word in procedure_lower for word in ["erro", "error", "código"]):
            return True
        elif any(word in procedure_lower for word in ["filtro", "filter", "limpeza"]):
            return True
        
        return False
    
    @kernel_function(
        name="execute_runbook",
        description="Execute an automated runbook"
    )
    async def execute_runbook(
        self,
        runbook_name: Annotated[str, "Name of the runbook to execute"],
        parameters: Annotated[Optional[str], "JSON string of parameters"] = None
    ) -> Annotated[str, "Execution result"]:
        """Execute a runbook.
        
        Args:
            runbook_name: Name of the runbook
            parameters: Optional parameters as JSON string
            
        Returns:
            Execution result
        """
        logger.info(f"Executing runbook: {runbook_name}")
        
        # Simulate runbook execution
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        
        # In a real system, this would actually execute the runbook
        # For now, we simulate success
        
        result = {
            "execution_id": execution_id,
            "runbook_name": runbook_name,
            "status": "success",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "steps_completed": 5,
            "steps_total": 5,
            "output": "Runbook executado com sucesso"
        }
        
        logger.info(f"Runbook execution completed: {result}")
        
        return execution_id
    
    def get_runbook_for_procedure(self, procedure_description: str) -> Optional[str]:
        """Get runbook name for a procedure (non-kernel function).
        
        Args:
            procedure_description: Description of the procedure
            
        Returns:
            Runbook name or None
        """
        desc_lower = procedure_description.lower()
        
        if any(word in desc_lower for word in ["reset", "reiniciar"]):
            return "reset_machine"
        elif any(word in desc_lower for word in ["erro", "error", "código"]):
            return "clear_error_code"
        elif any(word in desc_lower for word in ["filtro", "filter"]):
            return "filter_check"
        
        return None
    
    def build_runbook_execution_dict(
        self,
        runbook_name: str,
        procedure_description: str,
        success: bool = True,
        machine: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build runbook execution dictionary (non-kernel function).
        
        Args:
            runbook_name: Name of the runbook
            procedure_description: Description of the procedure
            success: Whether execution was successful
            machine: Optional machine identifier
            
        Returns:
            Runbook execution dictionary
        """
        execution_id = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        
        runbook_info = self.available_runbooks.get(runbook_name, {})
        steps = runbook_info.get("steps", [])
        
        return {
            "execution_id": execution_id,
            "runbook_name": runbook_name,
            "runbook_title": runbook_info.get("name", runbook_name),
            "procedure_description": procedure_description,
            "machine": machine,
            "success": success,
            "status": "completed" if success else "failed",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "steps": steps,
            "steps_completed": len(steps) if success else 0,
            "steps_total": len(steps),
            "estimated_time": runbook_info.get("estimated_time", "Desconhecido"),
            "output": "Procedimento executado com sucesso" if success else "Falha na execução",
            "logs": []
        }
