import logging
import os

LOG_FILE = "execution_trace.log"

def get_agent_logger(name: str) -> logging.Logger:
    """
    Configures and returns a centralized logger for LLMOps & Observability.
    Writes traces to execution_trace.log directly for all agents and tools.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s'
        )
        
        # Provide Observability via File Log
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Provide observability via stream output
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        
    return logger

def setup_logger():
    """
    Configures a centralized logger for LLMOps and observability.
    Logs standard input, tool calls, and outputs to execution_trace.log.
    """
    logging.basicConfig(
        filename='execution_trace.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("HR_MAS")

logger = setup_logger()
