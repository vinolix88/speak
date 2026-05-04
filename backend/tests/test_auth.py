import pytest
import uuid

@pytest.mark.asyncio
async def test_register_user(client):
    email = f"test_{uuid.uuid4()}@example.com"
    username = f"user_{uuid.uuid4().hex[:8]}"
    response = await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "Test123!"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email

@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    email = f"dup_{uuid.uuid4()}@example.com"
    username = f"dup_{uuid.uuid4().hex[:8]}"
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "Test123!"
    })
    response = await client.post("/api/v1/auth/register", json={
        "username": f"{username}_2",
        "email": email,
        "password": "Test123!"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

@pytest.mark.asyncio
async def test_login_success(client):
    email = f"login_{uuid.uuid4()}@example.com"
    username = f"login_{uuid.uuid4().hex[:8]}"
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "Test123!"
    })
    response = await client.post(f"/api/v1/auth/login?email={email}&password=Test123!")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = f"wrongpass_{uuid.uuid4()}@example.com"
    username = f"wrongpass_{uuid.uuid4().hex[:8]}"
    await client.post("/api/v1/auth/register", json={
        "username": username,
        "email": email,
        "password": "Test123!"
    })
    response = await client.post(f"/api/v1/auth/login?email={email}&password=WrongPass")
    assert response.status_code == 401