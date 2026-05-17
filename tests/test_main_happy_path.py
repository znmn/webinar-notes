import os
from pathlib import Path

from fastapi.testclient import TestClient

DB_FILE = Path(__file__).parent / "test_happy_path.db"
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE.as_posix()}"
os.environ["SECRET"] = "test-secret-key-32-bytes-minimum"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

import main  # noqa: E402


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def setup_module() -> None:
    main.Base.metadata.drop_all(bind=main.engine)
    main.Base.metadata.create_all(bind=main.engine)


def teardown_module() -> None:
    main.Base.metadata.drop_all(bind=main.engine)
    main.engine.dispose()
    if DB_FILE.exists():
        DB_FILE.unlink()


def test_happy_path_notes_crud() -> None:
    client = TestClient(main.app)

    register_res = client.post(
        "/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "secret123",
        },
    )
    assert register_res.status_code == 200
    login_res = client.post(
        "/login",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    create_res = client.post(
        "/notes",
        headers=_auth_header(token),
        json={
            "title": "First note",
            "description": "This is a note",
            "category": "work",
        },
    )
    assert create_res.status_code == 200
    created_note = create_res.json()["note"]
    note_id = created_note["id"]
    assert created_note["title"] == "First note"

    list_res = client.get("/notes", headers=_auth_header(token))
    assert list_res.status_code == 200
    payload = list_res.json()
    assert payload["count"] == 1
    assert payload["notes"][0]["id"] == note_id

    detail_res = client.get(f"/notes/{note_id}", headers=_auth_header(token))
    assert detail_res.status_code == 200
    assert detail_res.json()["title"] == "First note"

    update_res = client.put(
        f"/notes/{note_id}",
        headers=_auth_header(token),
        json={"title": "Updated title", "category": "learning"},
    )
    assert update_res.status_code == 200
    updated_note = update_res.json()["note"]
    assert updated_note["title"] == "Updated title"
    assert updated_note["category"] == "learning"

    delete_res = client.delete(
        f"/notes/{note_id}", headers=_auth_header(token)
    )
    assert delete_res.status_code == 200
    assert delete_res.json()["deleted_id"] == note_id

    list_after_delete_res = client.get("/notes", headers=_auth_header(token))
    assert list_after_delete_res.status_code == 200
    assert list_after_delete_res.json()["count"] == 0


def test_notes_access_isolated_per_user() -> None:
    client = TestClient(main.app)

    user1_register = client.post(
        "/register",
        json={
            "name": "Bob",
            "email": "bob@example.com",
            "password": "secret123",
        },
    )
    assert user1_register.status_code == 200
    user1_login = client.post(
        "/login",
        json={"email": "bob@example.com", "password": "secret123"},
    )
    assert user1_login.status_code == 200
    token_user1 = user1_login.json()["access_token"]

    user2_register = client.post(
        "/register",
        json={
            "name": "Charlie",
            "email": "charlie@example.com",
            "password": "secret123",
        },
    )
    assert user2_register.status_code == 200
    user2_login = client.post(
        "/login",
        json={"email": "charlie@example.com", "password": "secret123"},
    )
    assert user2_login.status_code == 200
    token_user2 = user2_login.json()["access_token"]

    create_res = client.post(
        "/notes",
        headers=_auth_header(token_user1),
        json={
            "title": "Private note",
            "description": "owned by bob",
            "category": "work",
        },
    )
    assert create_res.status_code == 200
    note_id = create_res.json()["note"]["id"]

    user2_list = client.get("/notes", headers=_auth_header(token_user2))
    assert user2_list.status_code == 200
    assert user2_list.json()["count"] == 0

    user2_detail = client.get(
        f"/notes/{note_id}", headers=_auth_header(token_user2)
    )
    assert user2_detail.status_code == 404

    user2_update = client.put(
        f"/notes/{note_id}",
        headers=_auth_header(token_user2),
        json={"title": "hacked"},
    )
    assert user2_update.status_code == 404

    user2_delete = client.delete(
        f"/notes/{note_id}", headers=_auth_header(token_user2)
    )
    assert user2_delete.status_code == 404
