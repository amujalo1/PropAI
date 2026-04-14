"""CI tests"""
import pytest


def test_create_ci(client):
    """Test CI creation"""
    response = client.post(
        "/ci",
        json={
            "type": "Location",
            "region": "SA",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["type"] == "Location"
    assert data["region"] == "SA"
    assert data["ci_id"].startswith("PROP-")


def test_create_ci_with_parent(client):
    """Test CI creation with parent"""
    # Create parent
    parent_response = client.post(
        "/ci",
        json={
            "type": "Location",
            "region": "SA",
        },
    )
    parent_id = parent_response.json()["id"]

    # Create child
    response = client.post(
        "/ci",
        json={
            "type": "Complex",
            "region": "SA",
            "parent_id": parent_id,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["parent_id"] == parent_id
    assert data["hierarchy_level"] == 2


def test_get_ci(client):
    """Test get CI by ID"""
    # Create CI
    create_response = client.post(
        "/ci",
        json={
            "type": "Location",
            "region": "SA",
        },
    )
    ci_id = create_response.json()["ci_id"]

    # Get CI
    response = client.get(f"/ci/{ci_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ci_id"] == ci_id


def test_get_ci_hierarchy(client):
    """Test get CI hierarchy"""
    # Create hierarchy
    loc_response = client.post(
        "/ci",
        json={
            "type": "Location",
            "region": "SA",
        },
    )
    loc_id = loc_response.json()["id"]

    complex_response = client.post(
        "/ci",
        json={
            "type": "Complex",
            "region": "SA",
            "parent_id": loc_id,
        },
    )
    complex_ci_id = complex_response.json()["ci_id"]

    # Get hierarchy
    response = client.get(f"/ci/hierarchy/{complex_ci_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["type"] == "Location"
    assert data[1]["type"] == "Complex"
