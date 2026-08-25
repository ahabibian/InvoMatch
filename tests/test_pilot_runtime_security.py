from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient

from invomatch.config.settings import load_application_settings
from invomatch.config.validation import validate_application_settings
from invomatch.main import create_app


PILOT_TOKENS = """[
  {"token":"pilot-viewer-credential","user_id":"pilot-viewer","username":"pilot-viewer","role":"viewer","status":"active","tenant_id":"pilot-tenant"},
  {"token":"pilot-operator-credential","user_id":"pilot-operator","username":"pilot-operator","role":"operator","status":"active","tenant_id":"pilot-tenant"},
  {"token":"pilot-inactive-credential","user_id":"pilot-inactive","username":"pilot-inactive","role":"viewer","status":"inactive","tenant_id":"pilot-tenant"}
]"""


def _client(tmp_path: Path, monkeypatch, *, secure_cookie: bool = False) -> TestClient:
    monkeypatch.setenv("INVOMATCH_ENV", "local")
    monkeypatch.setenv("INVOMATCH_SECURITY_SEED_TOKENS_JSON", PILOT_TOKENS)
    monkeypatch.setenv("INVOMATCH_SESSION_COOKIE_SECURE", str(secure_cookie).lower())
    monkeypatch.setenv("INVOMATCH_AUDIT_EVENT_DB_PATH", str(tmp_path / "audit.sqlite3"))
    monkeypatch.setenv("INVOMATCH_INPUT_SESSION_DB_PATH", str(tmp_path / "input.sqlite3"))
    app = create_app(
        run_store_path=tmp_path / "runs.sqlite3",
        review_store_path=tmp_path / "reviews.sqlite3",
        export_base_dir=tmp_path / "exports",
    )
    return TestClient(app)


def test_production_and_staging_require_external_credentials(monkeypatch) -> None:
    for environment in ("staging", "production"):
        monkeypatch.setenv("INVOMATCH_ENV", environment)
        monkeypatch.delenv("INVOMATCH_SECURITY_SEED_TOKENS_JSON", raising=False)
        settings = load_application_settings()
        result = validate_application_settings(settings)
        assert result.is_valid is False
        assert "security.seed_tokens_json must not be empty when auth is enabled" in result.errors


def test_production_rejects_committed_demo_credentials(monkeypatch) -> None:
    monkeypatch.setenv("INVOMATCH_ENV", "production")
    monkeypatch.setenv(
        "INVOMATCH_SECURITY_SEED_TOKENS_JSON",
        '[{"token":"viewer-token","user_id":"viewer","username":"viewer","role":"viewer","status":"active","tenant_id":"pilot"}]',
    )
    result = validate_application_settings(load_application_settings())
    assert result.is_valid is False
    assert "staging and production must not use committed demo tokens" in result.errors


def test_local_environment_retains_explicit_demo_convenience(monkeypatch) -> None:
    monkeypatch.setenv("INVOMATCH_ENV", "local")
    monkeypatch.delenv("INVOMATCH_SECURITY_SEED_TOKENS_JSON", raising=False)
    result = validate_application_settings(load_application_settings())
    assert result.is_valid is True


def test_valid_login_creates_httponly_session_and_authorizes_api(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)

    login = client.post(
        "/api/auth/login",
        json={"credential": "pilot-viewer-credential"},
    )
    assert login.status_code == 200
    cookie = login.headers["set-cookie"].lower()
    assert "httponly" in cookie
    assert "samesite=strict" in cookie
    assert "max-age=3600" in cookie
    assert "secure" not in cookie

    session = client.get("/api/auth/session")
    assert session.status_code == 200
    assert session.json()["user"]["username"] == "pilot-viewer"

    queue = client.get("/api/review/queue")
    assert queue.status_code == 200


def test_production_cookie_posture_sets_secure_attribute(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch, secure_cookie=True)
    login = client.post(
        "/api/auth/login",
        json={"credential": "pilot-viewer-credential"},
    )
    assert login.status_code == 200
    assert "secure" in login.headers["set-cookie"].lower()


def test_invalid_and_inactive_login_are_rejected(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    invalid = client.post("/api/auth/login", json={"credential": "wrong"})
    inactive = client.post(
        "/api/auth/login",
        json={"credential": "pilot-inactive-credential"},
    )
    assert invalid.status_code == 401
    assert inactive.status_code == 403


def test_logout_revokes_session(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    assert client.post(
        "/api/auth/login", json={"credential": "pilot-viewer-credential"}
    ).status_code == 200
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/session").status_code == 401


def test_session_preserves_backend_authorization(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    client.post("/api/auth/login", json={"credential": "pilot-viewer-credential"})
    denied = client.get("/api/operations/metrics")
    assert denied.status_code == 403


def test_cors_is_explicit_and_never_wildcard(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("INVOMATCH_ALLOWED_ORIGINS", "https://pilot.example.test")
    client = _client(tmp_path, monkeypatch)

    allowed = client.options(
        "/api/auth/session",
        headers={
            "Origin": "https://pilot.example.test",
            "Access-Control-Request-Method": "GET",
        },
    )
    denied = client.options(
        "/api/auth/session",
        headers={
            "Origin": "https://untrusted.example.test",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert allowed.headers["access-control-allow-origin"] == "https://pilot.example.test"
    assert "access-control-allow-origin" not in denied.headers


def test_readiness_returns_503_for_unwritable_dependency(tmp_path, monkeypatch) -> None:
    client = _client(tmp_path, monkeypatch)
    settings = client.app.state.application_settings
    missing = tmp_path / "missing-artifact-root"
    client.app.state.application_settings = replace(
        settings,
        storage=replace(settings.storage, artifact_root_path=missing),
    )

    response = client.get("/readiness")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert "storage_unwritable:missing-artifact-root" in response.json()["dependency_errors"]


def test_frontend_source_has_no_bundled_bearer_secret_dependency() -> None:
    source = Path("ui/invomatch-ui/src/services/api.ts").read_text(encoding="utf-8")
    assert "VITE_API_AUTH_TOKEN" not in source
    assert 'credentials: "same-origin"' in source


def test_pilot_composition_declares_private_backend_and_state_mount() -> None:
    composition = Path("docker-compose.pilot.yml").read_text(encoding="utf-8")
    assert "pilot_state:/var/lib/invomatch" in composition
    assert 'INVOMATCH_SCHEDULER_ENABLED: "false"' in composition
    assert "pilot credentials must be supplied externally" in composition
    backend_section = composition.split("  frontend:", 1)[0]
    assert "ports:" not in backend_section


def test_host_override_replaces_frontend_publish_with_loopback_only_binding() -> None:
    override = Path("docker-compose.pilot-host.yml").read_text(encoding="utf-8")
    assert "ports: !override" in override
    assert '127.0.0.1:${INVOMATCH_PILOT_PORT:-8080}:8080' in override
    assert "0.0.0.0" not in override


def test_pilot_environment_template_is_non_secret_and_launch_safe() -> None:
    template = Path("pilot.env.example").read_text(encoding="utf-8")
    assert "INVOMATCH_SECURITY_SEED_TOKENS_JSON=\n" in template
    assert "INVOMATCH_SESSION_COOKIE_SECURE=true" in template
    assert "INVOMATCH_RELEASE_VALIDATION_STATUS=controlled_pilot" in template
    assert ".env.pilot" in Path(".gitignore").read_text(encoding="utf-8")

