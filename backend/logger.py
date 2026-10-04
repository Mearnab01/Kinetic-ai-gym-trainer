import logging
import os
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-5s | %(message)s"
DATE_FORMAT = "%H:%M:%S"

logging.addLevelName(logging.WARNING, "WARN")

LOG_TRACEBACK = os.environ.get("LOG_TRACEBACK", "false").lower() in ("1", "true", "yes")

logger = logging.getLogger("kinetic")

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.propagate = False

    uvicorn_error = logging.getLogger("uvicorn.error")
    uvicorn_error.handlers.clear()
    uvicorn_error.addHandler(handler)
    uvicorn_error.setLevel(logging.INFO)
    uvicorn_error.propagate = False

    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()
    uvicorn_access.propagate = False
    uvicorn_access.disabled = True
    
    uvicorn_root = logging.getLogger("uvicorn")
    uvicorn_root.handlers.clear()
    uvicorn_root.addHandler(handler)
    uvicorn_root.setLevel(logging.INFO)
    uvicorn_root.propagate = False

    _configured = True


def log_exception(message: str, exc: BaseException) -> None:
    logger.error("%s: %s: %s", message, type(exc).__name__, exc, exc_info=LOG_TRACEBACK)


configure_logging()