"""Tests for the FastAPI application."""


class TestHealth:
    def test_health_returns_200(self, client, caplog):
        response = client.get("/health")
        assert "Health check called" in caplog.text
        assert response.status_code == 200

    def test_health_payload(self, client):
        response = client.get("/health")
        assert response.json() == {"status": "ok"}


class TestItems:
    def test_list_items_empty(self, client):
        response = client.get("/items")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_item(self, create_item):
        response = create_item()
        data = response.json()

        assert response.status_code == 201
        assert data == {
            "id": 1,
            "name": "Widget",
            "description": None,
            "price": 9.99,
        }

    def test_create_item_with_description(self, create_item):
        response = create_item(
            name="Gadget",
            description="A cool gadget",
            price=19.99,
        )

        assert response.status_code == 201
        assert response.json()["description"] == "A cool gadget"

    def test_get_existing_item(self, client, create_item):
        create_item()

        response = client.get("/items/1")

        assert response.status_code == 200
        assert response.json()["name"] == "Widget"

    def test_get_missing_item_returns_404(self, client):
        response = client.get("/items/999")
        assert response.status_code == 404

    def test_list_items_after_create(self, client, create_item):
        create_item(name="A", price=1.0)
        create_item(name="B", price=2.0)

        response = client.get("/items")

        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_delete_item(self, client, create_item):
        create_item(name="ToDelete", price=0.01)

        response = client.delete("/items/1")

        assert response.status_code == 204
        assert client.get("/items/1").status_code == 404

    def test_delete_missing_item_returns_404(self, client):
        response = client.delete("/items/999")
        assert response.status_code == 404

    def test_create_item_invalid_price_returns_422(self, client):
        response = client.post(
            "/items", json={"name": "Bad Price", "price": -5.0}
        )
        assert response.status_code == 422

    def test_create_item_empty_name_returns_422(self, client):
        response = client.post("/items", json={"name": "", "price": 10.0})
        assert response.status_code == 422

    def test_get_item_invalid_path_id_returns_422(self, client):
        response = client.get("/items/0")
        assert response.status_code == 422

