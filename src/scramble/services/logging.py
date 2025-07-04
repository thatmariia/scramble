import os
import sys
import logging

LOG_FORMAT = '[%(asctime)s][%(filename)s][%(lineno)d] %(levelname)s: %(message)s'


def configure_logging(log_file: str, verbose: bool, silent: bool):
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
