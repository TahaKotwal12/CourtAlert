# src/utils/logger.py
import logging
import os

def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger with both console and file handlers.
    In serverless environments (like Vercel), only console logging is used.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Set logging level and format
        logger.setLevel(logging.DEBUG)

        # Formatter for logs
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        formatter = logging.Formatter(log_format)

        # Console Handler (always available)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File Handler - only in local development
        # Check for serverless environment indicators
        is_serverless = (
            os.environ.get('VERCEL') == '1' or 
            os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None or
            os.environ.get('FUNCTION_TARGET') is not None or
            os.environ.get('K_SERVICE') is not None
        )
        
        if not is_serverless:
            try:
                # Only try file logging in non-serverless environments
                LOG_DIR = "logs"
                os.makedirs(LOG_DIR, exist_ok=True)
                
                file_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"))
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
            except (OSError, PermissionError, FileNotFoundError):
                # Silently skip file logging if not possible
                pass

        # Avoid duplicated logs
        logger.propagate = False

    return logger
