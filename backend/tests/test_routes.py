"""Testes para os endpoints da API."""
import pytest


def test_login_success(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_tickets_unauthorized(client):
    response = client.get("/api/tickets")
    assert response.status_code == 403


def test_list_tickets_authorized(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/tickets", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_analytics_unauthorized(client):
    response = client.get("/api/analytics")
    assert response.status_code == 403


def test_analytics_authorized(client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    response = client.get("/api/analytics", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "resolved_by_ai_percent" in data
    assert "success_rate_percent" in data
