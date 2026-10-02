import hashlib
from app.config import settings

def test_payhere_webhook_success_callback(client):
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
    amount_str = f"{order['total_amount']:.2f}"

    # 2. Compute authentic PayHere md5sig for status_code = 2
    merchant_id = settings.PAYHERE_MERCHANT_ID
    currency = "LKR"
    status_code = "2"
    hashed_secret = hashlib.md5(settings.PAYHERE_MERCHANT_SECRET.encode("utf-8")).hexdigest().upper()
    sig_raw = f"{merchant_id}{order_number}{amount_str}{currency}{status_code}{hashed_secret}"
    valid_md5sig = hashlib.md5(sig_raw.encode("utf-8")).hexdigest().upper()

    # 3. Simulate PayHere POST to notify_url with x-www-form-urlencoded
    form_payload = {
        "merchant_id": merchant_id,
        "order_id": order_number,
        "payment_id": "320025999888",
        "payhere_amount": amount_str,
        "payhere_currency": currency,
        "status_code": status_code,
        "md5sig": valid_md5sig,
        "method": "VISA",
        "status_message": "Payment verified"
    }

    notify_res = client.post(
        "/api/v1/payments/payhere/notify",
        data=form_payload
    )
    assert notify_res.status_code == 200

    # 4. Check order status is now PAID
    check_res = client.get(f"/api/v1/orders/{order_number}")
    updated_order = check_res.json()
    assert updated_order["status"] == "PAID"
    assert len(updated_order["payments"]) == 1
    assert updated_order["payments"][0]["signature_valid"] is True

def test_payhere_webhook_invalid_signature_rejection(client):
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

    # 2. Tampered signature
    form_payload = {
        "merchant_id": settings.PAYHERE_MERCHANT_ID,
        "order_id": order_number,
        "payment_id": "FAKE_ID",
        "payhere_amount": f"{order['total_amount']:.2f}",
        "payhere_currency": "LKR",
        "status_code": "2",
        "md5sig": "INVALID_SIGNATURE_ATTACK",
        "method": "VISA"
    }

    notify_res = client.post("/api/v1/payments/payhere/notify", data=form_payload)
    assert notify_res.status_code == 400

    # Verify order is still PENDING
    check_res = client.get(f"/api/v1/orders/{order_number}")
    assert check_res.json()["status"] == "PENDING"

def test_simulator_endpoint(client):
    # Create order
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
    order_number = create_res.json()["order_number"]

    # Call simulator
    sim_res = client.post("/api/v1/payments/simulate", json={
        "order_number": order_number,
        "status_code": 2,
        "method": "VISA",
        "status_message": "Automated simulator test"
    })
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["success"] is True
    assert sim_data["order_status"] == "PAID"
    assert sim_data["signature_valid"] is True
