import hashlib
from app.services.payhere_service import PayHereService

def test_generate_checkout_hash_calculation():
    merchant_id = "1211149"
    order_id = "ORD-TEST-1234"
    amount = 2500.5  # Should format to 2500.50
    currency = "LKR"
    merchant_secret = "4TkZ76v6Ea48qW6wQ3X5F1G2"

    computed_hash = PayHereService.generate_checkout_hash(
        merchant_id=merchant_id,
        order_id=order_id,
        amount=amount,
        currency=currency,
        merchant_secret=merchant_secret
    )

    # Step-by-step verification
    hashed_secret = hashlib.md5(merchant_secret.encode('utf-8')).hexdigest().upper()
    expected_raw = f"{merchant_id}{order_id}2500.50{currency}{hashed_secret}"
    expected_hash = hashlib.md5(expected_raw.encode('utf-8')).hexdigest().upper()

    assert computed_hash == expected_hash
    assert len(computed_hash) == 32
    assert computed_hash.isupper()

def test_verify_payhere_signature_valid():
    merchant_id = "1211149"
    order_id = "ORD-TEST-9999"
    payhere_amount = "3400.00"
    payhere_currency = "LKR"
    status_code = "2"
    merchant_secret = "4TkZ76v6Ea48qW6wQ3X5F1G2"

    # Compute valid signature
    hashed_secret = hashlib.md5(merchant_secret.encode('utf-8')).hexdigest().upper()
    sig_raw = f"{merchant_id}{order_id}{payhere_amount}{payhere_currency}{status_code}{hashed_secret}"
    valid_md5sig = hashlib.md5(sig_raw.encode('utf-8')).hexdigest().upper()

    is_valid, calc_sig = PayHereService.verify_payhere_signature(
        merchant_id=merchant_id,
        order_id=order_id,
        payhere_amount=payhere_amount,
        payhere_currency=payhere_currency,
        status_code=status_code,
        received_md5sig=valid_md5sig,
        merchant_secret=merchant_secret
    )

    assert is_valid is True
    assert calc_sig == valid_md5sig

def test_verify_payhere_signature_tampered():
    merchant_id = "1211149"
    order_id = "ORD-TEST-9999"
    payhere_amount = "10.00"  # Attacker changed amount from 3400 to 10
    payhere_currency = "LKR"
    status_code = "2"
    merchant_secret = "4TkZ76v6Ea48qW6wQ3X5F1G2"
    fake_md5sig = "FAKE0000000000000000000000000000"

    is_valid, _ = PayHereService.verify_payhere_signature(
        merchant_id=merchant_id,
        order_id=order_id,
        payhere_amount=payhere_amount,
        payhere_currency=payhere_currency,
        status_code=status_code,
        received_md5sig=fake_md5sig,
        merchant_secret=merchant_secret
    )

    assert is_valid is False
