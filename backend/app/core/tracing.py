"""Langfuse tracing — wraps key operations with trace spans.
Langfuse Cloud is free for 50k observations/mo — same SDK as self-host.
"""
import logging
from contextlib import contextmanager
from langfuse import Langfuse
from app.config import settings

logger = logging.getLogger(__name__)

_langfuse: Langfuse | None = None


class _BestEffortSpan:
    def __init__(self, span: object, name: str) -> None:
        self._span = span
        self._name = name

    def update(self, **values: object) -> None:
        try:
            update = getattr(self._span, "update")
            update(**values)
        except Exception:
            logger.exception("Could not update Langfuse span '%s'", self._name)


def get_langfuse() -> Langfuse | None:
    global _langfuse
    if _langfuse is None:
        if not (
            settings.langfuse_host
            and settings.langfuse_public_key
            and settings.langfuse_secret_key
        ):
            if any(
                (
                    settings.langfuse_host,
                    settings.langfuse_public_key,
                    settings.langfuse_secret_key,
                )
            ):
                logger.warning(
                    "Langfuse tracing disabled: host, public key, and secret key "
                    "must all be configured"
                )
            return None

        try:
            _langfuse = Langfuse(
                host=settings.langfuse_host,
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
            )
        except Exception:
            logger.exception("Could not initialize Langfuse; tracing is disabled")
            return None

        print(f"Langfuse tracing enabled → {settings.langfuse_host}")
    return _langfuse


@contextmanager
def trace(name: str):
    """Context manager wrapping a code block as a Langfuse span."""
    lf = get_langfuse()
    if lf is None:
        yield None
        return

    try:
        if hasattr(lf, "start_as_current_observation"):
            span_context = lf.start_as_current_observation(name=name, as_type="span")
        else:
            span_context = lf.span(name=name)
        span = span_context.__enter__()
    except Exception:
        logger.exception("Could not start Langfuse span '%s'", name)
        yield None
        return

    try:
        yield _BestEffortSpan(span, name) if span is not None else None
    except BaseException as error:
        try:
            span_context.__exit__(type(error), error, error.__traceback__)
        except Exception:
            logger.exception("Could not close Langfuse span '%s'", name)
        raise
    else:
        try:
            span_context.__exit__(None, None, None)
        except Exception:
            logger.exception("Could not close Langfuse span '%s'", name)