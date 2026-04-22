import logging

LOG_FILE = "execution_trace.log"

# Prevent root logger from propagating and causing duplicates
logging.getLogger().setLevel(logging.WARNING)

def get_agent_logger(name: str) -> logging.Logger:
    """
    Configures and returns a named logger for LLMOps & Observability.
    Writes structured traces to execution_trace.log for all agents and tools.
    Each logger is created once; repeated calls return the same cached instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        logger.propagate = False  # Stops duplicate bubbling to root logger

        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        )

        # File handler — persists full execution trace for observability
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Stream handler — provides real-time console visibility
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
