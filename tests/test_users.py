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
