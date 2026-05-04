import pytest
import uuid

@pytest.mark.asyncio
async def test_create_private_chat(client):
    email1 = f"chat1_{uuid.uuid4()}@example.com"
    username1 = f"chat1_{uuid.uuid4().hex[:8]}"
    r1 = await client.post("/api/v1/auth/register", json={
        "username": username1,
        "email": email1,
        "password": "Test123!"
    })
    user1_id = r1.json()["id"]
    email2 = f"chat2_{uuid.uuid4()}@example.com"
    username2 = f"chat2_{uuid.uuid4().hex[:8]}"
    r2 = await client.post("/api/v1/auth/register", json={
        "username": username2,
        "email": email2,
        "password": "Test123!"
    })
    user2_id = r2.json()["id"]
    login = await client.post(f"/api/v1/auth/login?email={email1}&password=Test123!")
    token = login.json()["access_token"]
    response = await client.post("/api/v1/chats", json={
        "type": "private",
        "participant_ids": [user2_id]
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "private"
    assert data["name"] == username2

@pytest.mark.asyncio
async def test_get_user_chats(client):
    email1 = f"chats1_{uuid.uuid4()}@example.com"
    username1 = f"chats1_{uuid.uuid4().hex[:8]}"
    r1 = await client.post("/api/v1/auth/register", json={
        "username": username1,
        "email": email1,
        "password": "Test123!"
    })
    user1_id = r1.json()["id"]
    email2 = f"chats2_{uuid.uuid4()}@example.com"
    username2 = f"chats2_{uuid.uuid4().hex[:8]}"
    r2 = await client.post("/api/v1/auth/register", json={
        "username": username2,
        "email": email2,
        "password": "Test123!"
    })
    user2_id = r2.json()["id"]
    login = await client.post(f"/api/v1/auth/login?email={email1}&password=Test123!")
    token = login.json()["access_token"]
    await client.post("/api/v1/chats", json={
        "type": "private",
        "participant_ids": [user2_id]
    }, headers={"Authorization": f"Bearer {token}"})
    response = await client.get("/api/v1/chats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    chats = response.json()
    assert len(chats) > 0
    assert chats[0]["type"] == "private"