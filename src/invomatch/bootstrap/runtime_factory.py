from dataclasses import dataclass

from invomatch.config.models import ApplicationSettings


@dataclass(frozen=True)
class RuntimeDependencies:
    lease_seconds: int
    retry_budget: int
    stuck_run_timeout_seconds: int
    recovery_scan_interval_seconds: int
    scheduler_enabled: bool
    startup_repair_enabled: bool
    startup_validation_enabled: bool


def build_runtime_dependencies(settings: ApplicationSettings) -> RuntimeDependencies:
    return RuntimeDependencies(
        lease_seconds=settings.runtime.lease_seconds,
        retry_budget=settings.runtime.retry_budget,
        stuck_run_timeout_seconds=settings.runtime.stuck_run_timeout_seconds,
        recovery_scan_interval_seconds=settings.runtime.recovery_scan_interval_seconds,
        scheduler_enabled=settings.scheduler.scheduler_enabled,
        startup_repair_enabled=settings.runtime.startup_repair_enabled,
        startup_validation_enabled=settings.runtime.startup_validation_enabled,
    )