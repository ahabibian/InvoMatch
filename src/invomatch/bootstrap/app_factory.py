from dataclasses import dataclass

from invomatch.config.settings import load_application_settings
from invomatch.config.validation import StartupValidationResult
from .persistence_factory import (
    PersistenceDependencies,
    build_persistence_dependencies,
)
from .runtime_factory import RuntimeDependencies, build_runtime_dependencies
from .storage_factory import StorageDependencies, build_storage_dependencies
from .validation_factory import validate_startup_configuration


@dataclass(frozen=True)
class ConfiguredApplicationDependencies:
    persistence: PersistenceDependencies
    storage: StorageDependencies
    runtime: RuntimeDependencies
    validation: StartupValidationResult


def create_configured_app() -> ConfiguredApplicationDependencies:
    settings = load_application_settings()
    validation = validate_startup_configuration(settings)
    if not validation.is_valid:
        raise ValueError(
            "Invalid startup configuration: " + "; ".join(validation.errors)
        )

    return ConfiguredApplicationDependencies(
        persistence=build_persistence_dependencies(settings),
        storage=build_storage_dependencies(settings),
        runtime=build_runtime_dependencies(settings),
        validation=validation,
    )