from dataclasses import replace

from invomatch.bootstrap.storage_factory import build_storage_dependencies
from invomatch.config.settings import load_application_settings
from invomatch.services.storage.local_storage import LocalArtifactStorage


def test_build_storage_dependencies_uses_settings_export_directory(monkeypatch, tmp_path):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    storage = replace(
        settings.storage,
        export_directory=tmp_path / "exports",
        artifact_root_path=tmp_path / "artifacts",
        upload_root_path=tmp_path / "uploads",
        temp_directory=tmp_path / "tmp",
        log_directory=tmp_path / "logs",
    )
    settings = replace(settings, storage=storage)

    deps = build_storage_dependencies(settings)

    assert deps.export_root == tmp_path / "exports"
    assert isinstance(deps.artifact_storage, LocalArtifactStorage)


def test_build_storage_dependencies_honors_export_base_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("INVOMATCH_ENV", "local")

    settings = load_application_settings()
    override_export_root = tmp_path / "override-exports"

    deps = build_storage_dependencies(
        settings,
        export_base_dir=override_export_root,
    )

    assert deps.export_root == override_export_root
    assert isinstance(deps.artifact_storage, LocalArtifactStorage)