"""Cosmos DB service for work order operations.

This module provides a service layer for interacting with Azure Cosmos DB,
following best practices for connection management, error handling, and retry logic.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from azure.cosmos import CosmosClient, PartitionKey, exceptions
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy
from azure.identity import DefaultAzureCredential

from models.work_order import WorkOrder, WorkOrderCreate
from config.settings import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class CosmosDBError(Exception):
    """Custom exception for Cosmos DB operations."""
    pass


class CosmosService:
    """Service for Cosmos DB operations on work orders.
    
    This service implements the singleton pattern to maintain a single
    connection pool and follows Azure best practices for Cosmos DB access.
    """
    
    _instance: Optional['CosmosService'] = None
    _client: Optional[CosmosClient] = None
    _database: Optional[DatabaseProxy] = None
    _container: Optional[ContainerProxy] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Cosmos DB service."""
        if not hasattr(self, '_initialized'):
            # Get settings from centralized configuration
            settings = get_settings()
            
            self._endpoint = settings.cosmos_endpoint
            self._key = settings.cosmos_key
            self._database_name = settings.cosmos_database_name
            self._container_name = settings.cosmos_container_name
            
            if not self._endpoint:
                raise ValueError("COSMOS_ENDPOINT is required")
            
            self._initialized = True
            logger.info(
                f"CosmosService initialized for database '{self._database_name}', "
                f"container '{self._container_name}'"
            )
    
    def _get_client(self) -> CosmosClient:
        """Get or create Cosmos DB client.
        
        Returns:
            CosmosClient instance
        """
        if self._client is None:
            try:
                # Use key-based authentication
                if not self._key:
                    raise ValueError("COSMOS_KEY is required")
                
                self._client = CosmosClient(
                    url=self._endpoint,
                    credential=self._key
                )
                logger.info("Connected to Cosmos DB using access key")
                    
            except Exception as e:
                logger.error(f"Failed to create Cosmos DB client: {e}")
                raise CosmosDBError(f"Failed to initialize Cosmos DB client: {e}")
        
        return self._client
    
    def _get_database(self) -> DatabaseProxy:
        """Get database proxy.
        
        Returns:
            DatabaseProxy instance
        """
        if self._database is None:
            client = self._get_client()
            try:
                self._database = client.get_database_client(self._database_name)
                # Verify database exists
                self._database.read()
                logger.info(f"Connected to database '{self._database_name}'")
            except exceptions.CosmosResourceNotFoundError:
                logger.error(f"Database '{self._database_name}' not found")
                raise CosmosDBError(f"Database '{self._database_name}' does not exist")
            except Exception as e:
                logger.error(f"Failed to access database: {e}")
                raise CosmosDBError(f"Failed to access database: {e}")
        
        return self._database
    
    def _get_container(self) -> ContainerProxy:
        """Get container proxy.
        
        Returns:
            ContainerProxy instance
        """
        if self._container is None:
            database = self._get_database()
            try:
                self._container = database.get_container_client(self._container_name)
                # Verify container exists
                self._container.read()
                logger.info(f"Connected to container '{self._container_name}'")
            except exceptions.CosmosResourceNotFoundError:
                logger.error(f"Container '{self._container_name}' not found")
                raise CosmosDBError(f"Container '{self._container_name}' does not exist")
            except Exception as e:
                logger.error(f"Failed to access container: {e}")
                raise CosmosDBError(f"Failed to access container: {e}")
        
        return self._container
    
    async def create_work_order(self, work_order_data: WorkOrderCreate) -> WorkOrder:
        """Create a new work order in Cosmos DB.
        
        Args:
            work_order_data: Work order creation data
            
        Returns:
            Created WorkOrder object
            
        Raises:
            CosmosDBError: If creation fails
        """
        try:
            import uuid
            
            # Generate unique IDs
            document_id = str(uuid.uuid4())
            order_id = f"OS-{uuid.uuid4().hex[:8].upper()}"
            
            # Create full work order object with status-based partition key
            work_order = WorkOrder(
                id=document_id,
                order_id=order_id,
                partition_key=work_order_data.model_dump().get('status', 'pending'),
                **work_order_data.model_dump()
            )
            
            # Convert to Cosmos DB format
            document = work_order.to_cosmos_dict()
            
            # Insert into Cosmos DB
            container = self._get_container()
            created_item = container.create_item(body=document)
            
            logger.info(
                f"Work order created successfully: {order_id} (id: {document_id})"
            )
            
            # Return as WorkOrder object
            return WorkOrder(**created_item)
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB error creating work order: {e.message}")
            raise CosmosDBError(f"Failed to create work order: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error creating work order: {e}")
            raise CosmosDBError(f"Failed to create work order: {str(e)}")
    
    async def get_work_order(self, order_id: str) -> Optional[WorkOrder]:
        """Retrieve a work order by order_id.
        
        Args:
            order_id: Business order identifier (e.g., OS-ABC123)
            
        Returns:
            WorkOrder if found, None otherwise
        """
        try:
            container = self._get_container()
            
            # Query by order_id
            query = "SELECT * FROM c WHERE c.order_id = @order_id"
            parameters = [{"name": "@order_id", "value": order_id}]
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            if items:
                logger.info(f"Work order found: {order_id}")
                return WorkOrder(**items[0])
            
            logger.warning(f"Work order not found: {order_id}")
            return None
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB error retrieving work order: {e.message}")
            raise CosmosDBError(f"Failed to retrieve work order: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving work order: {e}")
            raise CosmosDBError(f"Failed to retrieve work order: {str(e)}")
    
    async def update_work_order_status(
        self,
        order_id: str,
        status: str,
        note: Optional[str] = None
    ) -> Optional[WorkOrder]:
        """Update work order status.
        
        Args:
            order_id: Business order identifier
            status: New status
            note: Optional note about the status change
            
        Returns:
            Updated WorkOrder if found, None otherwise
        """
        try:
            # First, get the work order
            work_order = await self.get_work_order(order_id)
            if not work_order:
                return None
            
            container = self._get_container()
            
            # Update fields
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Add note if provided
            if note:
                note_entry = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "type": "status_change",
                    "content": note,
                    "status": status
                }
                work_order.notes.append(note_entry)
                update_data["notes"] = work_order.notes
            
            # Update completed_at if status is completed
            if status == "completed":
                update_data["completed_at"] = datetime.utcnow().isoformat()
            
            # Merge updates
            work_order_dict = work_order.to_cosmos_dict()
            work_order_dict.update(update_data)
            
            # Replace item in Cosmos DB
            updated_item = container.replace_item(
                item=work_order.id,
                body=work_order_dict
            )
            
            logger.info(f"Work order status updated: {order_id} -> {status}")
            return WorkOrder(**updated_item)
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB error updating work order: {e.message}")
            raise CosmosDBError(f"Failed to update work order: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error updating work order: {e}")
            raise CosmosDBError(f"Failed to update work order: {str(e)}")
    
    async def list_work_orders(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 100
    ) -> List[WorkOrder]:
        """List work orders with optional filters.
        
        Args:
            status: Filter by status
            category: Filter by category
            priority: Filter by priority
            limit: Maximum number of results
            
        Returns:
            List of WorkOrder objects
        """
        try:
            container = self._get_container()
            
            # Build query
            conditions = []
            parameters = []
            
            if status:
                conditions.append("c.status = @status")
                parameters.append({"name": "@status", "value": status})
            
            if category:
                conditions.append("c.category = @category")
                parameters.append({"name": "@category", "value": category})
            
            if priority:
                conditions.append("c.priority = @priority")
                parameters.append({"name": "@priority", "value": priority})
            
            where_clause = " AND ".join(conditions) if conditions else "1=1"
            query = f"SELECT TOP {limit} * FROM c WHERE {where_clause} ORDER BY c.created_at DESC"
            
            items = list(container.query_items(
                query=query,
                parameters=parameters,
                enable_cross_partition_query=True
            ))
            
            logger.info(f"Retrieved {len(items)} work orders")
            return [WorkOrder(**item) for item in items]
            
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB error listing work orders: {e.message}")
            raise CosmosDBError(f"Failed to list work orders: {e.message}")
        except Exception as e:
            logger.error(f"Unexpected error listing work orders: {e}")
            raise CosmosDBError(f"Failed to list work orders: {str(e)}")
    
    def close(self):
        """Close Cosmos DB connections."""
        if self._client:
            # Cosmos Python SDK doesn't require explicit close
            logger.info("Cosmos DB service shutdown")
            self._client = None
            self._database = None
            self._container = None
