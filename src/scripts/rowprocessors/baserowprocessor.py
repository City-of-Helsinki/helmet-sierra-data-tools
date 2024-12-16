from threading import BoundedSemaphore
from concurrent.futures import ProcessPoolExecutor
import csv


class BaseRowProcessor(object):
    """Receives rows into queue and writes them into a file."""

    def __init__(self, outfile, dialect):
        self.outfile = open(outfile, 'w')
        self.outcsv = csv.writer(self.outfile, dialect=dialect)

    def __enter__(self):
        self.ppool = ProcessPoolExecutor(max_workers=10)
        self.pool_queue = BoundedSemaphore(100)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ppool.shutdown(wait=True, cancel_futures=False)
        self.outfile.close()

    def processkeys(self, param):
        self.outcsv.writerow(param)

    def processrow(self, param):
        self.pool_queue.acquire()
        fut = self.ppool.submit(self.rowprocessingworker, param)
        fut.add_done_callback(self.processed)

    @classmethod
    def rowprocessingworker(cls, param):
        return param

    def processed(self, param):
        self.pool_queue.release()
        try:
            result = param.result()
            self.outcsv.writerow(result)
        except Exception as e:
            print(e)
