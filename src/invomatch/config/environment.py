from enum import StrEnum


class EnvironmentName(StrEnum):
    LOCAL = "local"
    DEVELOPMENT = "development"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"