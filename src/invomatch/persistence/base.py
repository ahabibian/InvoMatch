from abc import ABC, abstractmethod


class RunStore(ABC):

    @abstractmethod
    def create_run(self):
        pass

    @abstractmethod
    def get_run(self, run_id: str):
        pass

    @abstractmethod
    def claim_next_run(self, worker_id: str):
        pass

    @abstractmethod
    def update_status(self, run_id: str, status: str):
        pass

    @abstractmethod
    def mark_terminal(self, run_id: str, status: str):
        pass