from invomatch.config.models import ApplicationSettings
from invomatch.config.validation import (
    StartupValidationResult,
    validate_application_settings,
)


def validate_startup_configuration(
    settings: ApplicationSettings,
) -> StartupValidationResult:
    return validate_application_settings(settings)