import logging
from logging import config

from api.views import router
from config.logging import LOGGING, configure_structlog_logger
from config.settings import settings
from fastapi import FastAPI, status

logging.basicConfig(level=logging.getLevelName(settings.LOGGING_LEVEL))
config.dictConfig(LOGGING)
configure_structlog_logger()

app = FastAPI(debug=settings.DEBUG)
app.include_router(router)


@app.get("/health-check/", status_code=status.HTTP_200_OK)
def health_check():
    return
