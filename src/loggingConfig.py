import logging
import time
import os
formatter = logging.Formatter('%(asctime)s %(name)-12s ' +
                              '%(levelname)-8s %(message)s')
log_debug = True


def setup_logger(name, log_file, level=logging.INFO, shownInConsole=False):
    """Function setup as many loggers as you want"""
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # If choose to show in termianl
    if shownInConsole:
        # define a Handler which writes info messages
        # or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(level)
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger(name).addHandler(console)

    return logger


CWD = os.getcwd()
LOG_DIR = CWD + '/logs_droneApiServer'
if not os.path.exists(LOG_DIR):
    print ("Making log directory: %s" % LOG_DIR)
    os.mkdir(LOG_DIR)
LOG_DIR_TODAY = LOG_DIR + '/' + time.strftime("%Y-%m-%d")
if not os.path.exists(LOG_DIR_TODAY):
    print ("Making log directory: %s" % LOG_DIR_TODAY)
    os.mkdir(LOG_DIR_TODAY)
"""
API_LOG_DIR = LOG_DIR + '/API_logs'
if not os.path.exists(API_LOG_DIR):
    os.mkdir(API_LOG_DIR)

MONITOR_LOG_DIR = LOG_DIR + '/monitor_logs'
if not os.path.exists(MONITOR_LOG_DIR):
    os.mkdir(MONITOR_LOG_DIR)
"""


if __name__ == '__main__':
    print (__doc__)
