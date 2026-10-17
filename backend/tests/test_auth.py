from fastapi.testclient import TestClient

PASSWORD = "correct horse battery staple"


def set_up(client: TestClient, password: str = PASSWORD) -> None:
    response = client.post("/api/auth/setup", json={"password": password})
    assert response.status_code == 204


def test_fresh_install_requires_setup(client: TestClient) -> None:
    response = client.get("/api/auth/status")

    assert response.json() == {"setup_required": True, "authenticated": False}


def test_setup_creates_the_owner_and_logs_them_in(client: TestClient) -> None:
    set_up(client)

    assert client.get("/api/auth/status").json() == {
        "setup_required": False,
        "authenticated": True,
    }
    assert client.get("/api/me").status_code == 200


def test_setup_is_refused_once_an_owner_exists(client: TestClient) -> None:
    set_up(client)

    response = client.post("/api/auth/setup", json={"password": "another password"})

    assert response.status_code == 409


def test_setup_rejects_a_short_password(client: TestClient) -> None:
    response = client.post("/api/auth/setup", json={"password": "short"})

    assert response.status_code == 422
    assert client.get("/api/auth/status").json()["setup_required"] is True


def test_login_with_the_right_password(client: TestClient) -> None:
    set_up(client)
    client.post("/api/auth/logout")

    response = client.post("/api/auth/login", json={"password": PASSWORD})

    assert response.status_code == 204
    assert client.get("/api/me").status_code == 200


def test_login_with_a_wrong_password_is_rejected(client: TestClient) -> None:
    set_up(client)
    client.post("/api/auth/logout")

    response = client.post("/api/auth/login", json={"password": "wrong password"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Incorrect password"}
    assert client.get("/api/me").status_code == 401


def test_login_before_setup_is_rejected(client: TestClient) -> None:
    response = client.post("/api/auth/login", json={"password": PASSWORD})

    assert response.status_code == 401


def test_session_cookie_is_http_only(client: TestClient) -> None:
    client.post("/api/auth/setup", json={"password": PASSWORD})

    response = client.post("/api/auth/login", json={"password": PASSWORD})

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("liasse_session=")
    assert "httponly" in cookie.lower()
    assert "samesite=lax" in cookie.lower()


def test_logout_ends_the_session(client: TestClient) -> None:
    set_up(client)

    response = client.post("/api/auth/logout")

    assert response.status_code == 204
    assert client.get("/api/me").status_code == 401
    assert client.get("/api/auth/status").json()["authenticated"] is False


def test_protected_routes_need_a_session(client: TestClient) -> None:
    set_up(client)
    client.cookies.clear()

    assert client.get("/api/me").status_code == 401


def test_health_and_auth_status_stay_public(client: TestClient) -> None:
    assert client.get("/api/health").status_code == 200
    assert client.get("/api/auth/status").status_code == 200
