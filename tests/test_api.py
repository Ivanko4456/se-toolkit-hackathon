"""Tests for the links API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_link(client: AsyncClient):
    """POST /api/links should create a link and return it."""
    payload = {
        "url": "https://example.com",
        "title": "Example Site",
        "tags": ["example", "test"],
        "user_id": "12345",
    }
    resp = await client.post("/api/links", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == "https://example.com/"
    assert data["title"] == "Example Site"
    assert data["tags"] == ["example", "test"]
    assert data["user_id"] == "12345"
    assert data["id"] is not None


@pytest.mark.asyncio
async def test_list_links(client: AsyncClient):
    """GET /api/links should return all links for a user."""
    # Create two links
    for i in range(2):
        await client.post("/api/links", json={
            "url": f"https://example.com/{i}",
            "title": f"Link {i}",
            "tags": ["python"] if i == 0 else ["java"],
            "user_id": "user1",
        })

    resp = await client.get("/api/links", params={"user_id": "user1"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["links"]) == 2


@pytest.mark.asyncio
async def test_list_links_filter_by_tag(client: AsyncClient):
    """GET /api/links?tag=python should filter by tag."""
    # Create links with different tags
    await client.post("/api/links", json={
        "url": "https://python.org",
        "title": "Python",
        "tags": ["python"],
        "user_id": "user2",
    })
    await client.post("/api/links", json={
        "url": "https://golang.org",
        "title": "Go",
        "tags": ["go"],
        "user_id": "user2",
    })

    resp = await client.get("/api/links", params={"user_id": "user2", "tag": "python"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["links"][0]["title"] == "Python"


@pytest.mark.asyncio
async def test_get_single_link(client: AsyncClient):
    """GET /api/links/{id} should return a single link."""
    create_resp = await client.post("/api/links", json={
        "url": "https://example.com/single",
        "title": "Single",
        "tags": ["test"],
        "user_id": "user3",
    })
    link_id = create_resp.json()["id"]

    resp = await client.get(f"/api/links/{link_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Single"


@pytest.mark.asyncio
async def test_delete_link(client: AsyncClient):
    """DELETE /api/links/{id} should delete a link if user_id matches."""
    create_resp = await client.post("/api/links", json={
        "url": "https://example.com/delete",
        "title": "Delete Me",
        "tags": ["test"],
        "user_id": "user4",
    })
    link_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/links/{link_id}", params={"user_id": "user4"})
    assert resp.status_code == 204

    # Verify deleted
    resp = await client.get(f"/api/links/{link_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_link_wrong_user(client: AsyncClient):
    """DELETE should fail if user_id doesn't match."""
    create_resp = await client.post("/api/links", json={
        "url": "https://example.com/protected",
        "title": "Protected",
        "tags": ["test"],
        "user_id": "owner",
    })
    link_id = create_resp.json()["id"]

    resp = await client.delete(f"/api/links/{link_id}", params={"user_id": "stranger"})
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """GET /health should return ok."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
