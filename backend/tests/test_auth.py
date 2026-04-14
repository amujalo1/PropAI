"""Authentication tests"""
import pytest
from app.models.user import User


def test_register_user(client):
    """Test user registration"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["name"] == "Test User"
    assert data["user"]["role"] == "agent"


def test_register_invalid_email(client):
    """Test registration with invalid email"""
    response = client.post(
        "/auth/register",
        json={
            "email": "invalid-email",
            "password": "testpass123",
            "name": "Test User",
        },
    )
    assert response.status_code == 422


def test_register_short_password(client):
    """Test registration with short password"""
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "short",
            "name": "Test User",
        },
    )
    assert response.status_code == 422


def test_login_user(client):
    """Test user login"""
    # Register first
    client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test User",
        },
    )

    # Login
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"]
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post(
        "/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


def test_logout(client):
    """Test logout"""
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"
