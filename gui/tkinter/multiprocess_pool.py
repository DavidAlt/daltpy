import multiprocessing as mp
#from multiprocessing import Pool
import time

def do_work(x):
    print(mp.current_process())
    time.sleep(2)
    return x+5

# Dummy data
dummy_data = [0,1,2,3,4,5,6,7,8,9,10,11]



if __name__ == '__main__':
    pool = mp.Pool() # automatically scales to the number of CPUs available

    # Send the data to the work list (==pool)
    results = pool.map(do_work, dummy_data)

    # Close the pool and wait for the work to finish
    #p.close()
    #p.join()

    # Print the results
    for result in results:
        print(result)