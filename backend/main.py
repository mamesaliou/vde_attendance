import os

import uvicorn
from app.__main__ import app
from app.core.logging import setup_logging, get_logger
from app.core.monitoring import init_monitoring

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
JSON_LOGS = os.getenv("JSON_LOGS", "true").lower() == "true"
setup_logging(log_level=LOG_LEVEL, json_logs=JSON_LOGS)

logger = get_logger(__name__)


def main():
    try:

        init_monitoring(app)

        config = uvicorn.Config(
            app,
            host=os.getenv("HOST", "0.0.0.0"),
            port=int(os.getenv("PORT", "8002")),
            reload=os.getenv("DEBUG", "true").lower() == "true",
            workers=int(os.getenv("WORKERS", "1")),
            log_level=LOG_LEVEL.lower(),
            proxy_headers=True,
            forwarded_allow_ips=os.getenv("FORWARDED_ALLOW_IPS", "*"),
            access_log=True
        )

        server = uvicorn.Server(config)
        logger.info(
            "starting_server",
            host=config.host,
            port=config.port,
            workers=config.workers,
            reload=config.reload,
        )
        server.run()

    except Exception as e:
        logger.error(
            "server_startup_error",
            error=str(e),
            exc_info=True
        )
        raise


if __name__ == "__main__":
    main()