"""Property tests"""
import pytest


def test_create_property(client):
    """Test property creation"""
    response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
            "description": "Test description",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Property"
    assert data["status"] == "DRAFT"


def test_create_property_missing_fields(client):
    """Test property creation with missing fields"""
    response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
        },
    )
    assert response.status_code == 422


def test_list_properties(client):
    """Test property listing"""
    # Create properties
    for i in range(3):
        client.post(
            "/properties",
            json={
                "name": f"Property {i}",
                "type": "residential",
                "location": "Test Location",
                "price": 100000.0 + i * 10000,
            },
        )

    response = client.get("/properties")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) == 3
    assert data["pagination"]["total"] == 3


def test_get_property(client):
    """Test get property by ID"""
    # Create property
    create_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = create_response.json()["id"]

    # Get property
    response = client.get(f"/properties/{property_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Property"


def test_get_nonexistent_property(client):
    """Test get nonexistent property"""
    response = client.get("/properties/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_update_property(client):
    """Test property update"""
    # Create property
    create_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = create_response.json()["id"]

    # Update property
    response = client.put(
        f"/properties/{property_id}",
        json={
            "name": "Updated Property",
            "status": "ACTIVE",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Property"
    assert data["status"] == "ACTIVE"


def test_delete_property(client):
    """Test property deletion"""
    # Create property
    create_response = client.post(
        "/properties",
        json={
            "name": "Test Property",
            "type": "residential",
            "location": "Test Location",
            "price": 100000.0,
        },
    )
    property_id = create_response.json()["id"]

    # Delete property
    response = client.delete(f"/properties/{property_id}")
    assert response.status_code == 204

    # Verify deletion
    response = client.get(f"/properties/{property_id}")
    assert response.status_code == 404
