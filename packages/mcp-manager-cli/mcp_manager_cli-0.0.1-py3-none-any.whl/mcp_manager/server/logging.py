import logging
from mcp_manager.server.globals import settings 

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(settings.LOG_FILE, mode='a', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers.clear()
        for handler in logging.getLogger().handlers:
            logger.addHandler(handler)
        logger.setLevel(logging.INFO) 