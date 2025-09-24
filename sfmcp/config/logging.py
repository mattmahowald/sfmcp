from __future__ import annotations
import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    # Very minimal logging - just errors to stderr
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
        force=True
    )

    # Only log our app, suppress other library logs
    logging.getLogger("sfmcp").setLevel(level)
    logging.getLogger("mcp").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
