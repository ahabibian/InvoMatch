from invomatch.services.release_identity_service import ReleaseIdentityService


def test_release_identity_falls_back_safely_when_metadata_missing(monkeypatch):
    for key in (
        "INVOMATCH_APPLICATION_NAME",
        "INVOMATCH_APPLICATION_VERSION",
        "INVOMATCH_RELEASE_COMMIT_SHA",
        "INVOMATCH_RELEASE_BRANCH",
        "INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC",
        "INVOMATCH_RELEASE_VALIDATION_STATUS",
    ):
        monkeypatch.delenv(key, raising=False)

    identity = ReleaseIdentityService(environment="local").get_release_identity()

    assert identity.application_name == "invomatch"
    assert identity.application_version == "0.1.0"
    assert identity.git_commit_sha == "unknown"
    assert identity.git_branch == "unknown"
    assert identity.build_timestamp_utc is None
    assert identity.environment == "local"
    assert identity.validation_status == "not_declared"
    assert identity.metadata_available is False


def test_release_identity_reads_only_explicit_safe_metadata(monkeypatch):
    monkeypatch.setenv("INVOMATCH_RELEASE_COMMIT_SHA", "abc123")
    monkeypatch.setenv("INVOMATCH_RELEASE_BRANCH", "main")
    monkeypatch.setenv("INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC", "2026-05-06T08:00:00Z")
    monkeypatch.setenv("INVOMATCH_RELEASE_VALIDATION_STATUS", "release_candidate_ready")
    monkeypatch.setenv("INVOMATCH_SECURITY_SEED_TOKENS_JSON", "secret-token-payload")

    identity = ReleaseIdentityService(environment="staging").get_release_identity()

    assert identity.application_name == "invomatch"
    assert identity.application_version == "0.1.0"
    assert identity.git_commit_sha == "abc123"
    assert identity.git_branch == "main"
    assert identity.build_timestamp_utc == "2026-05-06T08:00:00Z"
    assert identity.environment == "staging"
    assert identity.validation_status == "release_candidate_ready"
    assert identity.metadata_available is True

    exposed_values = identity.__dict__.values()
    assert "secret-token-payload" not in exposed_values


def test_release_identity_constructor_values_override_environment(monkeypatch):
    monkeypatch.setenv("INVOMATCH_RELEASE_COMMIT_SHA", "env-sha")
    monkeypatch.setenv("INVOMATCH_RELEASE_BRANCH", "env-branch")

    identity = ReleaseIdentityService(
        environment="test",
        application_name="custom-app",
        application_version="9.9.9",
        git_commit_sha="manual-sha",
        git_branch="manual-branch",
        build_timestamp_utc="2026-05-06T09:00:00Z",
        validation_status="manual-status",
    ).get_release_identity()

    assert identity.application_name == "custom-app"
    assert identity.application_version == "9.9.9"
    assert identity.git_commit_sha == "manual-sha"
    assert identity.git_branch == "manual-branch"
    assert identity.build_timestamp_utc == "2026-05-06T09:00:00Z"
    assert identity.environment == "test"
    assert identity.validation_status == "manual-status"
    assert identity.metadata_available is True

def test_release_identity_reads_ci_validation_metadata_without_release_ready_claim(monkeypatch):
    monkeypatch.setenv(
        "INVOMATCH_RELEASE_COMMIT_SHA",
        "c5120741111111111111111111111111111111111",
    )
    monkeypatch.setenv("INVOMATCH_RELEASE_BRANCH", "main")
    monkeypatch.delenv("INVOMATCH_RELEASE_BUILD_TIMESTAMP_UTC", raising=False)
    monkeypatch.setenv("INVOMATCH_RELEASE_VALIDATION_STATUS", "not_declared")

    identity = ReleaseIdentityService(environment="ci").get_release_identity()

    assert identity.git_commit_sha == "c5120741111111111111111111111111111111111"
    assert identity.git_branch == "main"
    assert identity.build_timestamp_utc is None
    assert identity.environment == "ci"
    assert identity.validation_status == "not_declared"
    assert identity.metadata_available is True
