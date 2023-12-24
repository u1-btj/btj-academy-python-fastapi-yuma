import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import User

PASSWORD="Test123!"
pw_bytes = PASSWORD.encode()
salt = bcrypt.gensalt()
hashed_pw = bcrypt.hashpw(
    password=pw_bytes,
    salt=salt,
)
USER = User(name="Test User", email="testuser@email.com", username="testuser", password=hashed_pw.decode())

async def setup_data(session: AsyncSession) -> None:    
    session.add_all([USER])
    await session.flush()

    await session.commit()

@pytest.mark.anyio
async def test_auth_viewsr(ac: AsyncClient, session: AsyncSession) -> None:
    # setup
    await setup_data(session)

    """Register"""
    users = await session.execute(select(User))
    users_count = len(users.scalars().all())

    payload = {
        "name": "Test Register", 
        "username": "testregister", 
        "email": "testregister@email.com", 
        "password": "TestRegister123!"
    }

    # execute
    response = await ac.post(
        "/api/v1/auth/register",
        json=payload,
    )

    print(response.content)
    assert 200 == response.status_code
    assert response.json()["data"]["username"] == payload["username"]

    users = await session.execute(select(User))

    assert users_count + 1 == len(users.scalars().all())

    """Login"""
    response = await ac.post(
        "/api/v1/auth/login",
        json={
            "username":"testuser",
            "password":PASSWORD
        }
    )
    assert 200 == response.status_code
    
    """Refresh Token"""
    REFRESH_TOKEN = response.json()["data"]["refresh_token"]
    response = await ac.get(
        "/api/v1/auth/refresh-token",
        headers={
            "Authorization": "Bearer " + REFRESH_TOKEN 
        }
    )

    assert 200 == response.status_code
    assert response.json()["data"]["access_token"] is not None

    """Change Password"""
    ACCESS_TOKEN = response.json()["data"]["access_token"]
    response = await ac.put(
        "/api/v1/auth/change-password",
        headers={
            "Authorization": "Bearer " + ACCESS_TOKEN 
        },
        json={
            "old_password":PASSWORD,
            "new_password":PASSWORD+"!"
        }
    )

    assert 200 == response.status_code
    