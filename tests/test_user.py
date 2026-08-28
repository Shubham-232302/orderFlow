
def test_create_user(client):
    response = client.post(
        "/api/v1/users",
        json = {
            "email": "abc@xyz.com",
            "name":"sss"
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
        "name": "user_1"
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
        "name": "user_1"
    }    
    
    resp = client.post(
        "/api/v1/users",
        json = user
    )
    
    assert resp.status_code == 422
