
def test_create_user(client):
    response = client.post(
        "/api/v1/users",
        json = {
            "email": "abc@xyz.com",
            "name":"sss",
             "password": "password123"
        }
    )
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == "abc@xyz.com"
    assert data["name"] == "sss"
    assert data["is_active"] == True
    assert "id" in data
    
    
    
def test_duplicate_email(client):
    user = {
        "email": "xyz@abc.com",
        "name": "user_1",
         "password": "password123"
    }
    
    first_user = client.post(
        "/api/v1/users",
        json = user
    )
    
    second_user = client.post(
        "/api/v1/users",
        json = user
    )
    
    assert first_user.status_code == 201
    assert second_user.status_code == 409
    
def test_invalid_email(client):
    user = {
        "email": "xyzabc.com",
        "name": "user_1",
        "password": "password123"
    }    
    
    resp = client.post(
        "/api/v1/users",
        json = user
    )
    
    assert resp.status_code == 422


def test_get_me(client):
    user = {
        "email": "me@example.com",
        "name": "me",
        "password": "password123",
    }

    create_response = client.post("/api/v1/users", json=user)
    assert create_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert login_response.status_code == 200

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )

    assert me_response.status_code == 200
    assert me_response.json()["email"] == user["email"]
