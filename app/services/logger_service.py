import asyncio
import logging
import os

from aiologger.handlers.files import (AsyncTimedRotatingFileHandler,
                                      RolloverInterval)


class AsyncioHandler(logging.StreamHandler):
    async def emit(self, record):
        await asyncio.to_thread(super().emit, record)


class LoggerService:
    def __init__(self, log_file_path=None, log_level=logging.INFO):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        if log_file_path:
            # Async File handler using aiologger
            log_file_path = os.path.abspath(log_file_path)
            handler = AsyncTimedRotatingFileHandler(
                log_file_path,
                # rotate logs every day at midnight
                when=RolloverInterval.MIDNIGHT,
                # save logs for 3 days
                backup_count=3,
                encoding='utf-8'
            )
        else:
            # Console handler
            handler = AsyncioHandler()

        handler.setLevel(log_level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
