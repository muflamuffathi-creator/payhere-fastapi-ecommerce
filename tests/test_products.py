def test_get_products(client):
    res = client.get("/api/v1/products")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert "name" in data[0]
    assert "price" in data[0]

def test_filter_products_by_category(client):
    res = client.get("/api/v1/products?category=Spices")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    for p in data:
        assert "Spices" in p["category"]

def test_search_products(client):
    res = client.get("/api/v1/products?search=Cinnamon")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    assert "cinnamon" in data[0]["name"].lower()

def test_create_and_delete_product(client):
    new_prod = {
        "name": "Artisanal Ceylon Vanilla Beans",
        "category": "Spices",
        "description": "Fragrant cured vanilla beans from Matale.",
        "price": 3500.0,
        "stock_quantity": 20,
        "badge": "Specialty"
    }
    create_res = client.post("/api/v1/products", json=new_prod)
    assert create_res.status_code == 201
    created = create_res.json()
    assert created["id"] is not None
    assert created["slug"] == "artisanal-ceylon-vanilla-beans"

    # Delete
    del_res = client.delete(f"/api/v1/products/{created['id']}")
    assert del_res.status_code == 204
