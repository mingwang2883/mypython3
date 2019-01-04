import logging
import os.path
import time

def set_up():
	logging.basicConfig(level=logging.DEBUG, format='\n''%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%Y/%m/%d %H:%M:%S',filename='log1.log')

set_up()
logger = logging.getLogger()
logger.debug('this is debug message')
logger.info('this is info message')
logger.warning('this is warning message')
