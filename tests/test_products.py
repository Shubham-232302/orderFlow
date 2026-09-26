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


def _login(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )


def _auth_headers(client, email, password):
    response = _login(client, email, password)
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


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
