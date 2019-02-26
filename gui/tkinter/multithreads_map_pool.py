# For logging
import logging
logging.basicConfig(level=logging.CRITICAL, format='%(levelname)-9s: %(name)s : %(funcName)s() : %(message)s')
log = logging.getLogger('map/pool')
log.setLevel(logging.DEBUG)

# For timing operations
from timeit import default_timer as timer
from functools import reduce

from multiprocessing.dummy import Pool as ThreadPool
import time


def format_elapsed_time(t):
        return "%d:%02d:%02d.%03d" % \
            reduce(lambda ll,b : divmod(ll[0],b) + ll[1:],
                [(t*1000,),1000,60,60])


def lengthy_func(x):
    time.sleep(2)
    return x+5


# Dummy data
data = [0,1,2,3,4,5,6,7,8,9,10,11]

# Make the pool of workers
num_workers = 12
pool = ThreadPool(num_workers)

t1 = timer()
results = pool.map(lengthy_func, data)


# Close the pool and wait for the work to finish
pool.close()
pool.join()
t2 = timer()

log.info(f'Total elapsed: {format_elapsed_time(t2-t1)}')
for result in results:
    print(result)