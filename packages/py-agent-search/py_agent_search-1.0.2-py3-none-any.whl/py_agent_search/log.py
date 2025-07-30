"""
This module sets up a logger that sends logs to a Loki instance.
Info: https://github.com/xente/loki-logger-handler
"""

import logging
import os
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler # Add this import, adjust module name if needed

LOKI_URL = os.getenv("LOKI_URL", "http://localhost:3100/loki/api/v1/push")
APP_ENV = os.getenv("APP_ENV", "production")

metadata_logger = {
    "loki_metadata": {}
}

# Set up logging
logger_name = "agent_search"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.INFO if APP_ENV == "production" else logging.DEBUG)

# Create an instance of the custom handler
logger_handler = LokiLoggerHandler(
    url=LOKI_URL,
    labels={
        "application": logger_name, 
        "environment": APP_ENV
    },
    label_keys={},
    timeout=10,
    enable_structured_loki_metadata=True,
    loki_metadata={"service": "user-service", "version": "1.0.0"},
    loki_metadata_keys=["thread_id"]
)
# Create an instance of the custom handler

logger.addHandler(logger_handler)
# mantiele il log anche su console
if os.getenv("APP_ENV") != "production":
    # Add a console handler for local development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
def send_log(message: str, metadata: dict = {}):
    """
    Set metadata for the callback handler.
    This can include any additional information you want to log.
    """
    metadata_logger["loki_metadata"] = metadata
    logger.debug(f"{message}", extra=metadata_logger)