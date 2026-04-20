from invomatch.config.environment import EnvironmentName
from invomatch.config.settings import load_application_settings


def test_load_application_settings_defaults_to_local(monkeypatch):
    monkeypatch.delenv("INVOMATCH_ENV", raising=False)

    settings = load_application_settings()
    export_dir = str(settings.storage.export_directory).replace("\\", "/")

    assert settings.environment == EnvironmentName.LOCAL
    assert settings.persistence.run_store_backend == "sqlite"
    assert settings.persistence.review_store_backend == "sqlite"
    assert export_dir.endswith("output/local/exports")


def test_load_application_settings_production_defaults(monkeypatch):
    monkeypatch.setenv("INVOMATCH_ENV", "production")

    settings = load_application_settings()

    assert settings.environment == EnvironmentName.PRODUCTION
    assert settings.scheduler.scheduler_enabled is True
    assert settings.observability.structured_logging_enabled is True
    assert settings.runtime.startup_validation_enabled is True