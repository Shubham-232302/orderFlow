import pytest

from app.api.dependencies import get_current_user, require_admin
from app.core.security import create_access_token, hash_password
from app.db.dependencies import get_db
from app.models.orders import Order
from app.models.product import Product
from app.models.user import User, UserRole
from app.schemas.orderItem import OrderItemCreate
from app.schemas.product import ProductCreate
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_service import AuthService
from app.services.order_service import OrderAccessDenied, OrderService
from app.services.product_service import ProductNotFoundError, ProductService
from app.services.user_service import UserServices


def _seed_user(db_session, email, name="user", password="password123", role=UserRole.USER, is_active=True):
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        is_active=is_active,
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_get_db_yields_and_closes_session():
    db_gen = get_db()
    db = next(db_gen)
    assert db is not None
    db_gen.close()


def test_get_current_user_rejects_invalid_token(client):
    invalid_token = create_access_token(999999)
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == 401

    bad_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer not-a-real-token"},
    )
    assert bad_response.status_code == 401


def test_require_admin_forbidden_for_non_admin(client):
    user_response = client.post(
        "/api/v1/users",
        json={"email": "regular@example.com", "name": "Regular", "password": "secret123"},
    )
    assert user_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "regular@example.com", "password": "secret123"},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    protected = client.get("/api/v1/users/", headers={"Authorization": f"Bearer {token}"})
    assert protected.status_code == 403


def test_user_service_update_delete_and_list(db_session):
    service = UserServices(db_session)
    created = service.create_user(UserCreate(email="update@example.com", name="Before", password="pw123"))

    updated = service.update_user(created.id, UserUpdate(name="After", email="new@example.com"))
    assert updated.name == "After"
    assert updated.email == "new@example.com"

    all_users = service.get_all_users()
    assert any(user.email == "new@example.com" for user in all_users)

    service.delete_user(created.id)
    with pytest.raises(Exception):
        service.get_user(created.id)


def test_auth_service_rejects_inactive_user(db_session):
    _seed_user(db_session, "inactive@example.com", "Inactive", "pw123", UserRole.USER, is_active=False)
    service = AuthService(db_session)

    with pytest.raises(ValueError, match="User is inactive"):
        service.login("inactive@example.com", "pw123")

    with pytest.raises(ValueError, match="Invalid email or password"):
        service.login("inactive@example.com", "wrong-password")


def test_product_service_missing_and_delete_paths(db_session):
    service = ProductService(db_session)

    with pytest.raises(ProductNotFoundError):
        service.get_product_by_id(999)

    created = service.create_product(ProductCreate(name="Keyboard", price=100, stock=4))
    service.delete_product(created.id)

    with pytest.raises(ProductNotFoundError):
        service.get_product_by_id(created.id)


def test_order_service_access_and_missing_product_paths(db_session):
    user1 = _seed_user(db_session, "owner@example.com", "Owner", "pw123")
    user2 = _seed_user(db_session, "other@example.com", "Other", "pw123")
    product = Product(name="Monitor", price=200, stock=5)
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)

    order = Order(user_id=user1.id, total_amount=400, idempotency_key="key-123")
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)

    service = OrderService(db_session)

    with pytest.raises(OrderAccessDenied):
        service.get_order_by_id(user2.id, order.id)

    assert service.get_order_by_id(user1.id, 99999) is None
    assert service.get_orders_by_user(user1.id)[0].id == order.id

    with pytest.raises(ProductNotFoundError):
        service.get_product_for_update(99999)

    schema = OrderItemCreate(product_id=product.id, quantity=2)
    assert schema.product_id == product.id
    assert schema.quantity == 2
