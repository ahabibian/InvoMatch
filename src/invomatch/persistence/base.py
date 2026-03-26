from abc import ABC, abstractmethod
from typing import Optional, List, Any
from datetime import datetime


class RunStore(ABC):
    """
    Backend-independent lifecycle persistence contract.

    This is NOT a simple CRUD interface.

    This abstraction represents the durable execution authority
    for reconciliation runs.
    """

    # -------------------------------------------------
    # Creation / Read
    # -------------------------------------------------

    @abstractmethod
    def create_run(self, run: Any) -> str:
        """
        Persist a new run.

        Must guarantee:
        - unique run_id
        - durable write
        - valid initial lifecycle state
        """
        raise NotImplementedError

    @abstractmethod
    def get_run(self, run_id: str) -> Optional[Any]:
        """
        Retrieve authoritative run state.
        """
        raise NotImplementedError

    @abstractmethod
    def list_runs(
        self,
        status: Optional[str] = None,
        tenant_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Any]:
        """
        Deterministically ordered run listing.
        """
        raise NotImplementedError

    # -------------------------------------------------
    # Claim Lifecycle
    # -------------------------------------------------

    @abstractmethod
    def claim_next_eligible_run(
        self,
        worker_id: str,
        now: datetime,
        lease_seconds: int,
    ) -> Optional[Any]:
        """
        Atomically claim next runnable run.
        Must prevent double claim.
        """
        raise NotImplementedError

    @abstractmethod
    def renew_claim(
        self,
        run_id: str,
        worker_id: str,
        now: datetime,
        lease_seconds: int,
    ) -> bool:
        """
        Extend lease for active owner.
        """
        raise NotImplementedError

    @abstractmethod
    def release_claim(
        self,
        run_id: str,
        worker_id: str,
    ) -> bool:
        """
        Explicit lease release.
        """
        raise NotImplementedError

    # -------------------------------------------------
    # Lifecycle Transitions
    # -------------------------------------------------

    @abstractmethod
    def update_progress(
        self,
        run_id: str,
        status: str,
        stage: Optional[str] = None,
    ) -> bool:
        """
        Durable lifecycle progress update.
        Must reject invalid transitions.
        """
        raise NotImplementedError

    @abstractmethod
    def mark_awaiting_review(self, run_id: str) -> bool:
        """
        Transition run to awaiting_review.
        """
        raise NotImplementedError

    @abstractmethod
    def mark_failed(
        self,
        run_id: str,
        error_code: Optional[str],
        error_message: Optional[str],
    ) -> bool:
        """
        Terminal failure write.
        """
        raise NotImplementedError

    @abstractmethod
    def mark_completed(
        self,
        run_id: str,
        result_uri: Optional[str],
    ) -> bool:
        """
        Terminal completion write.
        """
        raise NotImplementedError

    # -------------------------------------------------
    # Retry Semantics
    # -------------------------------------------------

    @abstractmethod
    def increment_retry(self, run_id: str) -> bool:
        """
        Persist retry attempt.
        """
        raise NotImplementedError

    @abstractmethod
    def is_retry_allowed(self, run_id: str) -> bool:
        """
        Storage-visible retry eligibility.
        """
        raise NotImplementedError