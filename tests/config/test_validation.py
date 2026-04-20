from dataclasses import replace
from pathlib import Path

from invomatch.config.environment import EnvironmentName
from invomatch.config.settings import load_application_settings
from invomatch.config.validation import validate_application_settings


def test_validate_application_settings_accepts_default_local(monkeypatch):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    result = validate_application_settings(settings)

    assert result.is_valid is True
    assert result.errors == ()


def test_validate_application_settings_rejects_non_positive_lease(monkeypatch):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    runtime = replace(settings.runtime, lease_seconds=0)
    settings = replace(settings, runtime=runtime)

    result = validate_application_settings(settings)

    assert result.is_valid is False
    assert "runtime.lease_seconds must be greater than zero" in result.errors


def test_validate_application_settings_rejects_scheduler_enabled_in_test(monkeypatch):
    monkeypatch.setenv("INVOMATCH_ENV", "test")
    monkeypatch.setenv("INVOMATCH_SCHEDULER_ENABLED", "true")

    settings = load_application_settings()
    result = validate_application_settings(settings)

    assert result.is_valid is False
    assert "scheduler must be disabled in test environment by default" in result.errors


def test_validate_application_settings_rejects_relative_output_paths_in_production(monkeypatch):
    monkeypatch.setenv("INVOMATCH_ENV", "production")

    settings = load_application_settings()
    persistence = replace(
        settings.persistence,
        run_store_path=Path("output/production/reconciliation_runs.sqlite3"),
    )
    settings = replace(settings, persistence=persistence)

    result = validate_application_settings(settings)

    assert result.is_valid is False
    assert "production paths must not use relative output directories" in result.errors