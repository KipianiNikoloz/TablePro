from __future__ import annotations

from typing import Protocol

from tablepro_backend.domain.connections import ConnectionTestRequest, ConnectionTestResult


class ConnectionTester(Protocol):
    def test(self, request: ConnectionTestRequest) -> ConnectionTestResult:
        """Attempt a small driver-native connectivity check."""
