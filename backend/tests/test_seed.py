from app.core import db as dbmod
from app.seed import seed
from tests.conftest import register


def test_seed_is_repeatable_and_isolated(client):
    other = register(client, "someone@example.com")
    with dbmod.SessionLocal() as s:
        seed(s)
        seed(s)  # second run resets instead of duplicating

    r = client.post("/api/v1/auth/login", data={"username": "sample@example.com", "password": "sample1234"})
    assert r.status_code == 200, r.text
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    assert client.get("/api/v1/transactions", headers=h).json()["total"] > 50
    assert len(client.get("/api/v1/subscriptions", headers=h).json()) == 5
    assert len(client.get("/api/v1/goals", headers=h).json()) == 3
    assert client.get("/api/v1/dashboard/summary", headers=h).status_code == 200

    # other users are untouched
    assert client.get("/api/v1/transactions", headers=other).json()["total"] == 0

