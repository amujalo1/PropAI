"""Incident tests"""
import pytest


def test_create_incident(client):
    """Test incident creation"""
    # Create property first
    prop_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = prop_response.json()["id"]

    # Create incident
    response = client.post(
        "/incidents",
        json={
            "title": "Test Incident",
            "description": "Test description",
            "property_id": property_id,
            "priority": "P1",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Incident"
    assert data["priority"] == "P1"
    assert data["status"] == "OPEN"


def test_create_incident_missing_fields(client):
    """Test incident creation with missing fields"""
    response = client.post(
        "/incidents",
        json={
            "title": "Test Incident",
            "priority": "P1",
        },
    )
    assert response.status_code == 422


def test_list_incidents(client):
    """Test incident listing"""
    # Create property
    prop_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = prop_response.json()["id"]

    # Create incidents
    for i in range(3):
        client.post(
            "/incidents",
            json={
                "title": f"Incident {i}",
                "description": f"Description {i}",
                "property_id": property_id,
                "priority": "P1",
            },
        )

    response = client.get("/incidents")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_incident(client):
    """Test get incident by ID"""
    # Create property
    prop_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = prop_response.json()["id"]

    # Create incident
    create_response = client.post(
        "/incidents",
        json={
            "title": "Test Incident",
            "description": "Test description",
            "property_id": property_id,
            "priority": "P1",
        },
    )
    incident_id = create_response.json()["id"]

    # Get incident
    response = client.get(f"/incidents/{incident_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Incident"


def test_get_nonexistent_incident(client):
    """Test get nonexistent incident"""
    response = client.get("/incidents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
