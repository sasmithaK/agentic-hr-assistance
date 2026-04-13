import logging

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
