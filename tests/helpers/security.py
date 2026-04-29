from invomatch.config.models import SecuritySettings
from invomatch.services.security.authentication_service import AuthenticationService
from invomatch.services.security.authorization_service import AuthorizationService
from invomatch.services.security.security_audit_service import InMemorySecurityAuditService
from invomatch.services.security.token_provider import StaticTokenProvider


TEST_TOKEN = "operator-token"
TEST_AUTH_HEADER = {"Authorization": f"Bearer {TEST_TOKEN}"}
TEST_TENANT_ID = "tenant-test"


def attach_test_security(app, *, tenant_id: str = TEST_TENANT_ID) -> None:
    seed_tokens_json = (
        '[{"token":"operator-token",'
        '"user_id":"test-user",'
        '"username":"test-operator",'
        '"role":"operator",'
        '"status":"active",'
        f'"tenant_id":"{tenant_id}"'
        '}]'
    )

    app.state.security_settings = SecuritySettings(
        auth_enabled=True,
        public_health_enabled=True,
        public_readiness_enabled=True,
        seed_tokens_json=seed_tokens_json,
        security_audit_enabled=True,
    )

    token_provider = StaticTokenProvider(seed_tokens_json)

    app.state.token_provider = token_provider
    app.state.authentication_service = AuthenticationService(token_provider=token_provider)
    app.state.authorization_service = AuthorizationService()
    app.state.security_audit_service = InMemorySecurityAuditService()