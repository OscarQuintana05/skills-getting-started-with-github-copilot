import os
import sys
from urllib.parse import quote

# Ensure src is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_unregister_flow():
    activity = "Chess Club"
    email = "pytest_user@example.com"
    enc = quote(activity, safe="")

    # Ensure clean start: remove if exists
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{enc}/participants?email={quote(email, safe='')}")

    # Signup
    resp = client.post(f"/activities/{enc}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Verify present
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should return 400
    resp = client.post(f"/activities/{enc}/signup?email={quote(email, safe='')}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{enc}/participants?email={quote(email, safe='')}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    # Verify removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
