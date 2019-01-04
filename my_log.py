import logging
import os.path
import time

def my_log(logger):
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    log_name = 'Order'
    log_path = os.getcwd() + '/log/'
    if not os.path.exists(log_path):
        os.system('mkdir '+ log_path)
    log_file = log_path + log_name + '.log'
    fh = logging.FileHandler(log_file, mode='a')
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter("\n""%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",datefmt  = '%Y-%m-%d %H:%M:%S')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

def a():
    #try:
    print(1/0)
    #except Exception as e:
        #print(e)
        #logger.error('error message',exc_info=True)

def my_test(logger):
    try:
        a()
        #print(t)
        logger.info('ok')
    except Exception as e:
        logger.error('this is a logger error message',exc_info=True)
    #logger.debug('this is a logger debug message')
    #logging.info('this is a logger info message')
    #logger.warning('this is a logger warning message')
    #logger.error('this is a logger error message')
    #logger.critical('this is a logger critical message')

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    #logger.setLevel(logging.DEBUG)
    my_log(logger)
    my_test(logger)
