import logging
from logging.handlers import TimedRotatingFileHandler
import os
formatter = logging.Formatter('%(asctime)s %(name)-12s ' +
                              '%(levelname)-8s %(message)s')
log_debug = True
# Unit of time interval
LOG_TIME_WHEN = "midnight"
# Chang log file interval
LOG_TIME_INTERVAL = 1
# Keep how many log files
LOG_BACKUP_NUM = 30


def setup_logger(name, log_file, level=logging.INFO, shownInConsole=False):
    """Function setup as many loggers as you want"""
    handler = TimedRotatingFileHandler(log_file,
                                       when=LOG_TIME_WHEN,
                                       interval=LOG_TIME_INTERVAL,
                                       backupCount=LOG_BACKUP_NUM)
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


if __name__ == '__main__':
    print (__doc__)
