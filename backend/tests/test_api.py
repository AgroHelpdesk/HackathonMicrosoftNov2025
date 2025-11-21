"""
Basic tests for the Agro Auto-Resolve API
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "Agro Auto-Resolve API is running"


def test_get_tickets():
    """Test getting all tickets"""
    response = client.get("/api/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_get_agents():
    """Test getting all agents"""
    response = client.get("/api/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 5


def test_get_runbooks():
    """Test getting all runbooks"""
    response = client.get("/api/runbooks")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_metrics():
    """Test getting metrics"""
    response = client.get("/api/metrics")
    assert response.status_code == 200
    assert "reduction" in response.json()
    assert "avgResolutionTime" in response.json()


def test_get_plots():
    """Test getting plots/talhoes"""
    response = client.get("/api/plots")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_chat_endpoint():
    """Test the chat endpoint"""
    response = client.post(
        "/api/chat",
        json={"message": "Test message", "ticketId": "T-001"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
    assert "agent" in response.json()
    assert "ts" in response.json()


def test_chat_fungus_detection():
    """Test chat with fungus keyword"""
    response = client.post(
        "/api/chat",
        json={"message": "I see fungus on my plants"}
    )
    assert response.status_code == 200
    assert "fungal" in response.json()["response"].lower()


def test_chat_vibration_detection():
    """Test chat with vibration keyword"""
    response = client.post(
        "/api/chat",
        json={"message": "The machine has vibration"}
    )
    assert response.status_code == 200
    assert "vibration" in response.json()["response"].lower()
