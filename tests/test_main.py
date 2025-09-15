from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)



def test_scan_secrets_invalid_url():
    print("[TEST #1] Running test_scan_secrets_invalid_url...")
    res = client.post("/scan/secrets", json={"repo_url": "ftp://bad.com/repo"})
    assert res.status_code == 422 or res.status_code == 400
    print("[TEST #1] test_scan_secrets_invalid_url passed: Properly rejected invalid repo URL.")

def test_scan_code_invalid_url():
    print("[TEST #2] Running test_scan_code_invalid_url...")
    res = client.post("/scan/code", json={"repo_url": "ssh://bad.com/repo"})
    assert res.status_code == 422 or res.status_code == 400
    print(f"[TEST #2] test_scan_code_invalid_url passed: Properly rejected invalid repo URL.")

def test_scan_secrets_success():
    print("[TEST #3] Running test_scan_secrets_success...")
    res = client.post(
        "/scan/secrets",
        json={"repo_url": "https://github.com/octocat/Hello-World"}
    )
    try:
        assert res.status_code == 200
        assert "report" in res.json()
        print("[TEST #3] test_scan_secrets_success passed: Scanned repo for secrets and returned report.")
    except AssertionError:
        print(f"[TEST #3] test_scan_secrets_success failed! Status: {res.status_code}, Response: {res.text}")
        raise

def test_scan_code_success():
    print("[TEST #4] Running test_scan_code_success...")
    res = client.post(
        "/scan/code",
        json={"repo_url": "https://github.com/octocat/Hello-World"}
    )
    try:
        assert res.status_code == 200
        assert "report" in res.json()
        print("[TEST #4] test_scan_code_success passed: Scanned repo for dangerous code usage and returned report.")
    except AssertionError:
        print(f"[TEST #4] test_scan_code_success failed! Status: {res.status_code}, Response: {res.text}")
        raise

