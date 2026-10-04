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


def test_user_login_rejects_bad_credentials(client):
    _create_user(client, "badlogin@example.com", "bad login")

    response = _login(client, "badlogin@example.com", "wrong-password")
    assert response.status_code == 401


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
