import logging

import click
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from ....framework.api.routers import metrics
from .context import lifespan
from .routes import chat_history

load_dotenv(dotenv_path=".env", verbose=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


@click.command()
@click.option("--hostname", default="0.0.0.0", help="hostname of the service")
@click.option("--port", default=8081, help="port")
@click.option("--log-level", type=click.STRING, default="INFO", help="log level (INFO, DEBUG, WARNING, ERROR, FATAL)")
def main(hostname: str, port: int, log_level: str):
    logger.setLevel(logging.getLevelName(log_level))

    logger.info("[Main] starting")
    app = FastAPI(lifespan=lifespan)

    logger.debug("[Main] adding metrics routes")
    app.include_router(metrics.router)

    logger.debug("[Main] adding git agent routes")
    app.include_router(chat_history.router)

    logger.info("[Main] online")

    uvicorn.run(app=app, host=hostname, port=port)


# Usage example
if __name__ == "__main__":
    main()
