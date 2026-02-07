"""
FILE: observability.py
STATUS: Active
RESPONSIBILITY: Logfire observability configuration and no-op fallback
LAST MAJOR UPDATE: 2026-02-06
MAINTAINER: Shahu
"""

import contextlib
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import logfire as _logfire

    logfire = _logfire
except ImportError:

    class _NoOpLogfire:
        """No-op fallback when logfire is not installed."""

        def instrument(self, *args: Any, **kwargs: Any):
            """Return a pass-through decorator."""

            def decorator(func):
                return func

            if args and callable(args[0]):
                return args[0]
            return decorator

        def span(self, *args: Any, **kwargs: Any):
            """Return a no-op context manager."""
            return contextlib.nullcontext()

        def configure(self, **kwargs: Any) -> None:
            """No-op configure."""

        def info(self, *args: Any, **kwargs: Any) -> None:
            """No-op log."""

        def instrument_pydantic_ai(self, **kwargs: Any) -> None:
            """No-op Pydantic AI instrumentation."""

    logfire = _NoOpLogfire()  # type: ignore[assignment]


def configure_observability() -> None:
    """Initialize Logfire observability.

    Configures Logfire with project settings and instruments
    Pydantic AI agents for tracing. Fails gracefully if Logfire
    is not installed or not configured.
    """
    try:
        from src.core.config import settings

        if not getattr(settings, "logfire_enabled", False):
            logger.debug("Logfire disabled in settings")
            return

        logfire.configure(
            service_name="sports-see",
            service_version="0.1.0",
        )
        logfire.instrument_pydantic_ai()
        logger.info("Logfire observability configured")

    except Exception as e:
        logger.warning("Failed to configure Logfire: %s", e)
