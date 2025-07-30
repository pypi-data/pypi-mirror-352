"""Telemetry module for Rizk SDK."""

import os
import sys
from typing import Dict, Any, Optional, ClassVar, cast

# Pass through to Traceloop's telemetry
from traceloop.sdk.telemetry import Telemetry as TraceloopTelemetry


class Telemetry:
    """Provides access to Rizk-specific telemetry capture.

    This class wraps the underlying Traceloop telemetry provider,
    prefixing events and adding Rizk-specific context. It follows
    a singleton pattern to ensure a single instance manages telemetry.

    Telemetry is enabled by setting the RIZK_TELEMETRY environment variable
    to "true". It is automatically disabled when running under pytest.
    """

    _instance: ClassVar[Optional["Telemetry"]] = None
    _telemetry_enabled: bool
    _traceloop_telemetry: TraceloopTelemetry

    def __new__(cls) -> "Telemetry":
        """Gets the singleton instance, creating it if necessary."""
        if cls._instance is None:
            instance = super(Telemetry, cls).__new__(cls)
            instance._telemetry_enabled = (
                os.getenv("RIZK_TELEMETRY", "false").lower() == "true"
            ) and "pytest" not in sys.modules
            instance._traceloop_telemetry = TraceloopTelemetry()
            cls._instance = instance
        return cls._instance

    def capture(
        self, event: str, event_properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """Captures a custom telemetry event if telemetry is enabled.

        Args:
            event: The name of the event (e.g., 'guardrails.decision').
                   It will be prefixed with 'rizk:'.
            event_properties: Optional dictionary of properties for the event.
                              The 'sdk': 'rizk-python' property is automatically added.
        """
        if self._telemetry_enabled:
            rizk_properties = {"sdk": "rizk-python", **(event_properties or {})}
            self._traceloop_telemetry.capture(f"rizk:{event}", rizk_properties)

    def log_exception(self, exception: Exception) -> None:
        """Logs an exception to telemetry if enabled.

        Args:
            exception: The exception instance to log.
        """
        if self._telemetry_enabled:
            self._traceloop_telemetry.log_exception(exception)

    def feature_enabled(self, key: str) -> bool:
        """Checks if a Rizk-specific feature flag is enabled via telemetry.

        Args:
            key: The feature key to check (e.g., 'new_parser').
                 It will be prefixed with 'rizk_'.

        Returns:
            bool: True if the feature flag is enabled, False otherwise or if
                  telemetry is disabled.
        """
        if self._telemetry_enabled:
            # Prefix with 'rizk_' to avoid conflicts with potential traceloop flags
            return cast(bool, self._traceloop_telemetry.feature_enabled(f"rizk_{key}"))
        return False
