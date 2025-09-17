import logging

def setup_logger(name: str = "house-predictor") -> logging.Logger:
    """Configures and returns a logger instance"""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    return logging.getLogger(name)
