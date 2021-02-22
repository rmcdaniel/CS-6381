'''
Election Application
'''
import signal
import threading
import time
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

class Watch():
    '''
    Watch class
    '''
    def __init__(self, address, port):
        self.current_leader = None
        self.lowest = None
        self.client = KazooClient(hosts='{}:{}'.format(address, port))
        self.client.start()
        self.client.ChildrenWatch('/brokers', self.watch)

    def watch(self, brokers):
        '''
        Called when tne brokers change
        '''
        print(brokers)
        lowest = self.lowest
        leader = self.current_leader
        for broker in brokers:
            try:
                (address, status) = self.client.get('/brokers/{}'.format(broker))
            except NoNodeError:
                continue
            if lowest is None or status.czxid < lowest:
                lowest = status.czxid
                leader = address.decode('utf-8')
        self.lowest = lowest
        self.current_leader = leader

    def leader(self):
        '''
        Get current leader
        '''
        return self.current_leader

if __name__ == '__main__':
    stopped = threading.Event()

    def handler(_signalnum, _frame):
        '''
        Signal handler
        '''
        stopped.set()

    signal.signal(signal.SIGINT, handler)

    watch = Watch('127.0.0.1', 2181)
    while not stopped.is_set():
        print(watch.leader())
        time.sleep(1)

    stopped.wait()
