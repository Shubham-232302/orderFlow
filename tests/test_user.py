from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.services.user_service import UserServices, UserNotFoundError


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
    response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "name": name,
            "password": password,
            "role": role.value,
        },
    )
    return response


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def _auth_headers(client, email, password):
    response = _login(client, email, password)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_create_user(client):
    response = _create_user(client, "abc@xyz.com", "sss")

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == "abc@xyz.com"
    assert data["name"] == "sss"
    assert data["is_active"] is True
    assert data["role"] == UserRole.USER.value
    assert "id" in data


def test_duplicate_email(client):
    user = {
        "email": "xyz@abc.com",
        "name": "user_1",
        "password": "password123",
    }

    first_user = client.post("/api/v1/users", json=user)
    second_user = client.post("/api/v1/users", json=user)

    assert first_user.status_code == 201
    assert second_user.status_code == 409


def test_invalid_email(client):
    user = {
        "email": "xyzabc.com",
        "name": "user_1",
        "password": "password123",
    }

    response = client.post("/api/v1/users", json=user)

    assert response.status_code == 422


def test_get_me(client):
    user = {
        "email": "me@example.com",
        "name": "me",
        "password": "password123",
    }

    create_response = client.post("/api/v1/users", json=user)
    assert create_response.status_code == 201

    login_response = _login(client, user["email"], user["password"])
    assert login_response.status_code == 200

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == user["email"]


def test_user_routes_admin_access_and_update(client, db_session):
    _seed_user(db_session, "admin@example.com", "Admin User", "adminpass", UserRole.ADMIN)

    auth = _auth_headers(client, "admin@example.com", "adminpass")
    users_response = client.get("/api/v1/users/", headers=auth)
    assert users_response.status_code == 200
    assert any(user["email"] == "admin@example.com" for user in users_response.json())

    target = _create_user(client, "target@example.com", "Target User")
    assert target.status_code == 201
    target_id = target.json()["id"]

    update_response = client.patch(
        f"/api/v1/users/{target_id}",
        json={"name": "Updated Target", "role": UserRole.ADMIN.value},
        headers=auth,
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Target"
    assert update_response.json()["role"] == UserRole.ADMIN.value

    delete_response = client.delete(f"/api/v1/users/{target_id}", headers=auth)
    assert delete_response.status_code == 204

    fetch_response = client.get(f"/api/v1/users/{target_id}", headers=auth)
    assert fetch_response.status_code == 404


def test_user_login_rejects_bad_credentials(client):
    _create_user(client, "badlogin@example.com", "bad login")

    response = _login(client, "badlogin@example.com", "wrong-password")
    assert response.status_code == 401


def test_user_service_create_and_fetch(db_session):
    service = UserServices(db_session)

    created = service.create_user(
        UserCreate(email="service@example.com", name="service-user", password="secret123")
    )

    assert created.id is not None
    assert created.email == "service@example.com"
    assert created.name == "service-user"
    assert created.is_active is True
    assert verify_password("secret123", created.password_hash)

    fetched = service.get_user(created.id)
    assert fetched.email == "service@example.com"


def test_user_service_raises_for_missing_user(db_session):
    service = UserServices(db_session)

    try:
        service.get_user(9999)
        assert False, "Expected UserNotFoundError"
    except UserNotFoundError:
        pass


def test_create_product_requires_admin_and_lists_products(client, db_session):
    _seed_user(db_session, "admin-product@example.com", "Admin Product", "adminpass", UserRole.ADMIN)
    auth = _auth_headers(client, "admin-product@example.com", "adminpass")

    create_response = client.post(
        "/api/v1/products",
        json={"name": "Laptop", "price": 1200, "stock": 8},
        headers=auth,
    )
    assert create_response.status_code == 201
    product = create_response.json()
    assert product["name"] == "Laptop"
    assert product["price"] == 1200
    assert product["stock"] == 8

    list_response = client.get("/api/v1/products/", headers=auth)
    assert list_response.status_code == 200
    assert any(item["name"] == "Laptop" for item in list_response.json())


def test_get_update_and_delete_product(client, db_session):
    _seed_user(db_session, "admin-product-2@example.com", "Admin Product 2", "adminpass", UserRole.ADMIN)
    auth = _auth_headers(client, "admin-product-2@example.com", "adminpass")

    created = client.post(
        "/api/v1/products",
        json={"name": "Mouse", "price": 50, "stock": 10},
        headers=auth,
    )
    assert created.status_code == 201
    product_id = created.json()["id"]

    fetch_response = client.get(f"/api/v1/products/{product_id}", headers=auth)
    assert fetch_response.status_code == 200
    assert fetch_response.json()["name"] == "Mouse"

    update_response = client.patch(
        f"/api/v1/products/{product_id}",
        json={"price": 75, "stock": 15},
        headers=auth,
    )
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 75
    assert update_response.json()["stock"] == 15

    delete_response = client.delete(f"/api/v1/products/{product_id}", headers=auth)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/products/{product_id}", headers=auth)
    assert missing_response.status_code == 404


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

    other_user = _create_user(client, "other@example.com", "Other User", "otherpass")
    assert other_user.status_code == 201
    other_auth = _auth_headers(client, "other@example.com", "otherpass")

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


def test_products_and_orders_require_authentication(client):
    protected_product = client.post(
        "/api/v1/products",
        json={"name": "No Auth", "price": 10, "stock": 2},
    )
    assert protected_product.status_code == 401

    protected_order = client.post(
        "/api/v1/orders/",
        json={"items": [{"product_id": 1, "quantity": 1}]},
        headers={"idempotency-key": "unauthenticated-key"},
    )
    assert protected_order.status_code == 401
