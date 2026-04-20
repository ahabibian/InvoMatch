from .loaders import load_settings_from_environment
from .models import ApplicationSettings


def load_application_settings() -> ApplicationSettings:
    return load_settings_from_environment()