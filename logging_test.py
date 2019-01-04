

import logging  
import os.path
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)  

#rq = time.strftime('%Y-%m-%d%-H-%M', time.localtime(time.time()))
rq = 'Order'
log_path = os.path.dirname(os.getcwd()) + '/code/' #+ 'Logs/'
print(log_path)
log_name = log_path + rq + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='w')
fh.setLevel(logging.DEBUG)  

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s",datefmt  = '%Y-%m-%d %H:%M:%S')
fh.setFormatter(formatter)

logger.addHandler(fh)


logger.debug('this is a logger debug message')
logger.info('this is a logger info message')
logger.warning('this is a logger warning message')
logger.error('this is a logger error message')
logger.critical('this is a logger critical message')
#logger.exception('???????')