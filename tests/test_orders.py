def test_create_order_success(client):
    order_data = {
        "first_name": "Fathima",
        "last_name": "Mufla",
        "email": "muflamuffathi@gmail.com",
        "phone": "+94771234567",
        "address": "45/2 Peradeniya Road",
        "city": "Kandy",
        "country": "Sri Lanka",
        "postal_code": "20000",
        "items": [
            {"product_id": 1, "quantity": 1}
        ]
    }
    res = client.post("/api/v1/orders", json=order_data)
    assert res.status_code == 201
    order = res.json()
    assert order["order_number"].startswith("ORD-")
    assert order["status"] == "PENDING"
    assert order["total_amount"] > 0
    assert len(order["items"]) == 1

def test_get_checkout_params_with_hash(client):
    # 1. Create order
    order_data = {
        "first_name": "Fathima",
        "last_name": "Mufla",
        "email": "muflamuffathi@gmail.com",
        "phone": "+94771234567",
        "address": "45/2 Peradeniya Road",
        "city": "Kandy",
        "country": "Sri Lanka",
        "items": [{"product_id": 1, "quantity": 1}]
    }
    create_res = client.post("/api/v1/orders", json=order_data)
    order = create_res.json()
    order_number = order["order_number"]

    # 2. Get checkout params
    params_res = client.get(f"/api/v1/orders/{order_number}/checkout-params")
    assert params_res.status_code == 200
    params = params_res.json()

    assert params["order_id"] == order_number
    assert "merchant_id" in params
    assert "hash" in params
    assert len(params["hash"]) == 32
    assert params["checkout_url"] == "https://sandbox.payhere.lk/pay/checkout"
