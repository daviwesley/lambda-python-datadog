"""Tests for the FastAPI application.

Run with:
    pytest tests/ -v
"""

from fastapi.testclient import TestClient

from app.main import app

# Use the synchronous TestClient (no need for pytest-asyncio for these tests)
client = TestClient(app, raise_server_exceptions=False)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class TestHealth:
    def test_health_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_payload(self):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# Items CRUD
# ---------------------------------------------------------------------------
class TestItems:
    def setup_method(self):
        """Reset the in-memory store before each test by recreating the counter."""
        from app.routes import items as items_module
        items_module._items.clear()
        items_module._counter = 0

    # -- list ----------------------------------------------------------------
    def test_list_items_empty(self):
        response = client.get("/items")
        assert response.status_code == 200
        assert response.json() == []

    # -- create --------------------------------------------------------------
    def test_create_item(self):
        payload = {"name": "Widget", "price": 9.99}
        response = client.post("/items", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Widget"
        assert data["price"] == 9.99
        assert data["description"] is None

    def test_create_item_with_description(self):
        payload = {"name": "Gadget", "description": "A cool gadget", "price": 19.99}
        response = client.post("/items", json=payload)
        assert response.status_code == 201
        assert response.json()["description"] == "A cool gadget"

    # -- get -----------------------------------------------------------------
    def test_get_existing_item(self):
        client.post("/items", json={"name": "Widget", "price": 9.99})
        response = client.get("/items/1")
        assert response.status_code == 200
        assert response.json()["name"] == "Widget"

    def test_get_missing_item_returns_404(self):
        response = client.get("/items/999")
        assert response.status_code == 404

    # -- list after create ---------------------------------------------------
    def test_list_items_after_create(self):
        client.post("/items", json={"name": "A", "price": 1.0})
        client.post("/items", json={"name": "B", "price": 2.0})
        response = client.get("/items")
        assert response.status_code == 200
        assert len(response.json()) == 2

    # -- delete --------------------------------------------------------------
    def test_delete_item(self):
        client.post("/items", json={"name": "ToDelete", "price": 0.01})
        response = client.delete("/items/1")
        assert response.status_code == 204
        assert client.get("/items/1").status_code == 404

    def test_delete_missing_item_returns_404(self):
        response = client.delete("/items/999")
        assert response.status_code == 404
