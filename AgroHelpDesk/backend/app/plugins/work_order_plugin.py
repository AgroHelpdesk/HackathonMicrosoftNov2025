"""Work Order plugin for Semantic Kernel.

This plugin provides work order creation and management capabilities.
Now with Cosmos DB persistence via Azure Functions (direct HTTP calls).
"""

import uuid
import asyncio
from datetime import datetime
from typing import Annotated, Dict, Any, Optional

import httpx
from semantic_kernel.functions import kernel_function

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("work_order_plugin")


class WorkOrderPlugin:
    """Plugin for work order creation and management.
    
    Persists work orders directly to Azure Functions API.
    """
    
    def __init__(self):
        """Initialize the plugin with Azure Functions configuration."""
        self.functions_url = settings.FUNCTIONS_URL.rstrip("/") if settings.FUNCTIONS_URL else "http://localhost:7071"
        self.function_key = settings.FUNCTIONS_KEY if hasattr(settings, 'FUNCTIONS_KEY') else None
        self.timeout = 30.0
        logger.info(f"WorkOrderPlugin initialized with Functions URL: {self.functions_url}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for Functions API.
        
        Returns:
            Dictionary of headers including auth if available
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.function_key:
            headers["x-functions-key"] = self.function_key
        return headers
    
    @kernel_function(
        name="create_work_order",
        description="Create a new work order for manual intervention and persist to Cosmos DB"
    )
    async def create_work_order(
        self,
        title: Annotated[str, "Work order title"],
        description: Annotated[str, "Detailed description of the issue"],
        category: Annotated[str, "Category of the work order"],
        priority: Annotated[str, "Priority level: baixa, media, alta"] = "media",
        machine: Annotated[Optional[str], "Machine identifier"] = None,
        location: Annotated[Optional[str], "Location or field"] = None
    ) -> Annotated[str, "Work order ID"]:
        """Create a new work order and persist to Cosmos DB.
        
        Args:
            title: Work order title
            description: Detailed description
            category: Category
            priority: Priority level
            machine: Optional machine identifier
            location: Optional location
            
        Returns:
            Work order ID
        """
        logger.info(
            f"Creating work order: category={category}, priority={priority}"
        )
        
        # Persist to Cosmos DB via Azure Functions (direct HTTP call)
        try:
            url = f"{self.functions_url}/api/workorders"
            payload = {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority,
                "assigned_specialist": "Técnico Geral",
                "estimated_time_hours": 2.0
            }
            
            # Add optional fields
            if machine:
                payload["machine_id"] = machine
            if location:
                payload["field_id"] = location
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self._get_headers()
                )
                
                if response.status_code == 201:
                    work_order = response.json().get("data", {})
                    work_order_id = work_order.get("order_id")
                    cosmos_id = work_order.get("id")
                    logger.info(
                        f"✅ Work order persisted to Cosmos DB: {work_order_id} "
                        f"(Cosmos ID: {cosmos_id})"
                    )
                    return work_order_id
                else:
                    # Fallback to local ID
                    work_order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
                    
                    # Log detailed error information
                    try:
                        error_body = response.json()
                        logger.error(
                            f"❌ Cosmos DB API Error - Status: {response.status_code}\n"
                            f"   URL: {url}\n"
                            f"   Response: {error_body}\n"
                            f"   Using local ID: {work_order_id}"
                        )
                    except Exception:
                        logger.error(
                            f"❌ Cosmos DB API Error - Status: {response.status_code}\n"
                            f"   URL: {url}\n"
                            f"   Response Text: {response.text}\n"
                            f"   Using local ID: {work_order_id}"
                        )
                    
                    return work_order_id
                    
        except httpx.TimeoutException:
            work_order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
            logger.error(
                f"❌ Timeout calling Azure Functions. Using local ID: {work_order_id}"
            )
            return work_order_id
        except httpx.RequestError as e:
            work_order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
            logger.error(
                f"❌ Request error calling Azure Functions: {e}. Using local ID: {work_order_id}"
            )
            return work_order_id
        except Exception as e:
            # Fallback: generate local ID on any error
            work_order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
            logger.error(
                f"❌ Error persisting to Cosmos DB: {e}. "
                f"Using local ID: {work_order_id}"
            )
            return work_order_id
    
    @kernel_function(
        name="format_work_order",
        description="Format work order details for display"
    )
    async def format_work_order(
        self,
        work_order_id: Annotated[str, "Work order ID"],
        title: Annotated[str, "Work order title"],
        description: Annotated[str, "Description"],
        priority: Annotated[str, "Priority level"]
    ) -> Annotated[str, "Formatted work order details"]:
        """Format work order details for user display.
        
        Args:
            work_order_id: Work order ID
            title: Title
            description: Description
            priority: Priority level
            
        Returns:
            Formatted work order text
        """
        priority_emoji = {
            "baixa": "🟢",
            "media": "🟡",
            "alta": "🔴"
        }
        
        emoji = priority_emoji.get(priority.lower(), "⚪")
        
        formatted = f"""
📋 **Ordem de Serviço Criada**

**ID:** {work_order_id}
**Título:** {title}
**Prioridade:** {emoji} {priority.upper()}

**Descrição:**
{description}

**Status:** Aguardando atribuição
**Criada em:** {datetime.now().strftime('%d/%m/%Y %H:%M')}

Um técnico será notificado e entrará em contato em breve.
"""
        
        return formatted.strip()
    
    def build_work_order_dict(
        self,
        title: str,
        description: str,
        category: str,
        priority: str = "media",
        machine: Optional[str] = None,
        location: Optional[str] = None,
        symptoms: Optional[str] = None,
        assigned_specialist: str = "Técnico de Campo",
        estimated_time_hours: float = 2.0,
        requester_id: Optional[str] = None,
        requester_contact: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build work order dictionary aligned with Cosmos DB schema.
        
        Args:
            title: Work order title
            description: Description
            category: Category
            priority: Priority level
            machine: Optional machine identifier
            location: Optional field/location identifier
            symptoms: Optional symptoms description
            assigned_specialist: Specialist to assign (default: Técnico de Campo)
            estimated_time_hours: Estimated completion time (default: 2.0)
            requester_id: Optional requester ID
            requester_contact: Optional requester contact info
            
        Returns:
            Work order dictionary matching Cosmos DB WorkOrder schema
        """
        work_order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
        cosmos_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        status = "pending"
        
        return {
            # Cosmos DB system fields
            "id": cosmos_id,
            "partition_key": status,  # Status-based partition key
            
            # Business fields
            "order_id": work_order_id,
            "title": title,
            "description": description,
            "category": category,
            "priority": priority,
            "status": status,
            "assigned_specialist": assigned_specialist,
            
            # Optional identifiers
            "machine_id": machine,
            "field_id": location,
            "symptoms": symptoms,
            "requester_id": requester_id,
            "requester_contact": requester_contact,
            
            # Time tracking
            "estimated_time_hours": estimated_time_hours,
            "created_at": now,
            "updated_at": now,
            "completed_at": None,
            
            # Collections
            "notes": [],
            "attachments": [],
            
            # Metadata
            "metadata": {}
        }
