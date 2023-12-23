import logging

from sqlalchemy.ext.declarative import declarative_base

from app.settings import settings

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.DEBUG if settings.DEBUG_MODE else logging.INFO)


Base = declarative_base()
