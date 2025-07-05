import os
import sys
import logging

LOG_FORMAT = '[%(asctime)s][%(filename)s][%(lineno)d] %(levelname)s: %(message)s'


def configure_logging(log_file: str, verbose: bool, silent: bool):
    """Configure logging settings.

    Args:
        log_file (str): Path to the log file.
        verbose (bool): Enable verbose logging.
        silent (bool): Suppress all output.
    """

    # ensure the logs directory exists
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # clear last log file
    if os.path.isfile(log_file):
        os.remove(log_file)

    logHandlers = []
    logHandlers.append(logging.FileHandler(log_file))
    if not silent:
        logHandlers.append(logging.StreamHandler(sys.stdout))

    if verbose:
        logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, handlers=logHandlers)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, handlers=logHandlers)
