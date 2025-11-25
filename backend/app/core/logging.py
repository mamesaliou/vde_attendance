import logging
import sys

import structlog
from pythonjsonlogger import json

def setup_logging(log_level: str = "INFO", json_logs: bool = True) -> None:
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format="%(message)s",
    )

    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if json_logs:
        formatter = json.JsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        
        root_logger = logging.getLogger()
        root_logger.handlers = [handler]
        
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True, sort_keys=True)
        )

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    return structlog.get_logger(name)
