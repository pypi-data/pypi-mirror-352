from typing import Protocol, runtime_checkable


@runtime_checkable
class SyntheraClientProtocol(Protocol):
    """Protocol defining the interface that FixedIncome needs from SyntheraClient."""

    def make_post_request(self, endpoint: str, payload: dict) -> dict:
        """Make a POST request to the Synthera API."""
        ...
