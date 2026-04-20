from pathlib import Path

from .environment import EnvironmentName

_DEFAULT_ALLOWED_INPUT_FORMATS = ("csv", "json")


def environment_root(environment: EnvironmentName) -> Path:
    if environment == EnvironmentName.PRODUCTION:
        return Path("/var/lib/invomatch")
    if environment == EnvironmentName.STAGING:
        return Path("output/staging")
    if environment == EnvironmentName.TEST:
        return Path("output/test")
    if environment == EnvironmentName.DEVELOPMENT:
        return Path("output/development")
    return Path("output/local")


def log_root(environment: EnvironmentName) -> Path:
    if environment == EnvironmentName.PRODUCTION:
        return Path("/var/log/invomatch")
    return environment_root(environment) / "logs"


def temp_root(environment: EnvironmentName) -> Path:
    if environment == EnvironmentName.PRODUCTION:
        return Path("/tmp/invomatch")
    return environment_root(environment) / "tmp"


def default_allowed_input_formats() -> tuple[str, ...]:
    return _DEFAULT_ALLOWED_INPUT_FORMATS