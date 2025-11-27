"""Validation utilities for work order operations."""

from typing import Dict, Any, List, Tuple
from models.work_order import WorkOrderCategory, WorkOrderPriority


def validate_work_order_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate work order data before processing.
    
    Args:
        data: Work order data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    required_fields = ["title", "description", "category", "assigned_specialist"]
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Validate title length
    if "title" in data:
        if len(data["title"]) < 3:
            errors.append("Title must be at least 3 characters long")
        if len(data["title"]) > 200:
            errors.append("Title must not exceed 200 characters")
    
    # Validate description length
    if "description" in data:
        if len(data["description"]) < 10:
            errors.append("Description must be at least 10 characters long")
        if len(data["description"]) > 2000:
            errors.append("Description must not exceed 2000 characters")
    
    # Validate category
    if "category" in data:
        valid_categories = [c.value for c in WorkOrderCategory]
        if data["category"] not in valid_categories:
            errors.append(
                f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
    
    # Validate priority if present
    if "priority" in data and data["priority"]:
        valid_priorities = [p.value for p in WorkOrderPriority]
        if data["priority"] not in valid_priorities:
            errors.append(
                f"Invalid priority. Must be one of: {', '.join(valid_priorities)}"
            )
    
    # Validate estimated_time_hours if present
    if "estimated_time_hours" in data and data["estimated_time_hours"] is not None:
        try:
            hours = float(data["estimated_time_hours"])
            if hours < 0.1 or hours > 1000:
                errors.append("Estimated time must be between 0.1 and 1000 hours")
        except (ValueError, TypeError):
            errors.append("Estimated time must be a valid number")
    
    # Validate string field lengths
    string_fields = {
        "machine_id": 50,
        "field_id": 50,
        "assigned_specialist": 100,
        "symptoms": 500,
        "requester_id": 100,
        "requester_contact": 100
    }
    
    for field, max_length in string_fields.items():
        if field in data and data[field]:
            if len(str(data[field])) > max_length:
                errors.append(f"{field} must not exceed {max_length} characters")
    
    return len(errors) == 0, errors


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """Sanitize string input.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Strip whitespace
    cleaned = str(value).strip()
    
    # Limit length
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned
