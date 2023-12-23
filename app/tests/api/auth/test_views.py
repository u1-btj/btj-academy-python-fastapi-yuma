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
async def test_register(ac: AsyncClient, session: AsyncSession) -> None:
    """Register"""
    # setup
    await setup_data(session)
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

@pytest.mark.anyio
async def test_login_refresh_token(ac: AsyncClient, session: AsyncSession) -> None:
    """Login and Refresh Token""" 

    await setup_data(session)
    import time
    time.sleep(2)
    # execute
    response = await ac.post(
        "/api/v1/auth/login",
        json={
            "username":"testuser",
            "password":PASSWORD
        }
    )
    
    REFRESH_TOKEN = response.json()["data"]["refresh_token"]
    response = await ac.get(
        "/api/v1/auth/refresh-token",
        headers={
            "Authorization": "Bearer " + REFRESH_TOKEN 
        }
    )

    assert 200 == response.status_code
    assert response.json()["data"]["access_token"] is not None


# @pytest.mark.anyio
# async def test_notes_update(ac: AsyncClient, session: AsyncSession) -> None:
#     """Update a note"""
#     from app.models import Notebook

#     # setup
#     await setup_data(session)
#     notebook = [nb async for nb in Notebook.read_all(session, include_notes=True)][0]
#     note = notebook.notes[0]
#     assert "Note 1" == note.title
#     assert "Content 1" == note.content

#     # execute
#     response = await ac.put(
#         f"/api/notes/{note.id}",
#         json={
#             "title": "Test Note",
#             "content": "Test Content",
#             "notebook_id": note.notebook_id,
#         },
#     )

#     print(response.content)
#     assert 200 == response.status_code
#     expected = {
#         "id": note.id,
#         "title": "Test Note",
#         "content": "Test Content",
#         "notebook_id": notebook.id,
#         "notebook_title": notebook.title,
#     }
#     assert expected == response.json()

#     await session.refresh(note)
#     assert "Test Note" == note.title
#     assert "Test Content" == note.content
