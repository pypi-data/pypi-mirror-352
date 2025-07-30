"""instrumentation.py"""
# pylint: disable=unused-import

try:
    from opentelemetry.trace import (
        get_current_span,
        get_tracer_provider,
    )
except ModuleNotFoundError:

    def get_current_span() -> None:
        """dummy current span"""

    def get_tracer_provider() -> None:
        """dummy trace provider"""
