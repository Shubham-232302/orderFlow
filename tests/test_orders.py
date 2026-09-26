from app.core.security import hash_password
from app.models.user import User, UserRole


def _seed_user(db_session, email, name="user", password="password123", role=UserRole.USER):
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        is_active=True,
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _create_user(client, email, name="user", password="password123", role=UserRole.USER):
    return client.post(
        "/api/v1/users",
        json={
            "email": email,
            "name": name,
            "password": password,
            "role": role.value,
        },
    )


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def _auth_headers(client, email, password):
    response = _login(client, email, password)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_order_flow_and_idempotency(client, db_session):
    _seed_user(db_session, "admin-order@example.com", "Admin Order", "adminpass", UserRole.ADMIN)
    admin_auth = _auth_headers(client, "admin-order@example.com", "adminpass")

    product_response = client.post(
        "/api/v1/products",
        json={"name": "Monitor", "price": 300, "stock": 5},
        headers=admin_auth,
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    buyer = _create_user(client, "buyer@example.com", "Buyer User", "buyerpass")
    assert buyer.status_code == 201
    buyer_auth = _auth_headers(client, "buyer@example.com", "buyerpass")

    order_payload = {"items": [{"product_id": product_id, "quantity": 2}]}
    first_order = client.post(
        "/api/v1/orders/",
        json=order_payload,
        headers={**buyer_auth, "idempotency-key": "key-1"},
    )
    assert first_order.status_code == 200, first_order.text
    data = first_order.json()
    assert data["total_amount"] == 600
    assert data["items"][0]["product_id"] == product_id
    assert data["items"][0]["quantity"] == 2

    duplicate_order = client.post(
        "/api/v1/orders/",
        json=order_payload,
        headers={**buyer_auth, "idempotency-key": "key-1"},
    )
    assert duplicate_order.status_code == 200
    assert duplicate_order.json()["id"] == data["id"]

    list_orders = client.get("/api/v1/orders/", headers=buyer_auth)
    assert list_orders.status_code == 200
    assert len(list_orders.json()) == 1

    other_user = _create_user(client, "other-order@example.com", "Other User", "otherpass")
    assert other_user.status_code == 201
    other_auth = _auth_headers(client, "other-order@example.com", "otherpass")

    forbidden = client.get(f"/api/v1/orders/{data['id']}", headers=other_auth)
    assert forbidden.status_code == 403


def test_order_rejects_invalid_stock_and_missing_product(client, db_session):
    _seed_user(db_session, "admin-order-2@example.com", "Admin Order 2", "adminpass", UserRole.ADMIN)
    admin_auth = _auth_headers(client, "admin-order-2@example.com", "adminpass")

    product_response = client.post(
        "/api/v1/products",
        json={"name": "Keyboard", "price": 80, "stock": 1},
        headers=admin_auth,
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    buyer = _create_user(client, "buyer-order-2@example.com", "Buyer 2", "buyerpass")
    assert buyer.status_code == 201
    buyer_auth = _auth_headers(client, "buyer-order-2@example.com", "buyerpass")

    insufficient_response = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": product_id, "quantity": 2}]},
        headers={**buyer_auth, "idempotency-key": "no-stock-key"},
    )
    assert insufficient_response.status_code == 409

    missing_response = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 999999, "quantity": 1}]},
        headers={**buyer_auth, "idempotency-key": "missing-product-key"},
    )
    assert missing_response.status_code == 404
