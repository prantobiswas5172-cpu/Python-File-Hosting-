import logging
import os

LOG_DIR = "logs_data"

def setup_logging():
    """Configures separate production-ready loggers."""
    os.makedirs(LOG_DIR, exist_ok=True)
    
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_format)
    root_logger.addHandler(console_handler)

    # Separate File Handlers
    log_files = {
        "bot": "bot.log",
        "hosting": "hosting.log",
        "user": "user.log",
        "admin": "admin.log",
        "error": "error.log"
    }

    for name, filename in log_files.items():
        handler = logging.FileHandler(os.path.join(LOG_DIR, filename), encoding='utf-8')
        handler.setFormatter(log_format)
        
        if name == "error":
            handler.setLevel(logging.ERROR)
            root_logger.addHandler(handler)
        else:
            handler.setLevel(logging.INFO)
            logger = logging.getLogger(name)
            logger.addHandler(handler)
            logger.propagate = False

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)