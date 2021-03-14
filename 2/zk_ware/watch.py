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
    def __init__(self, address, port, contenders):
        '''
        Constructor
        '''
        self._contenders = contenders
        self._leader = None
        self._leader_identifier = None
        self._zookeeper = KazooClient(hosts='{}:{}'.format(address, port))
        self._zookeeper.start()
        self._zookeeper.ChildrenWatch('/{}'.format(contenders), self.watch)

    def watch(self, contenders):
        '''
        Called when tne contenders change
        '''
        if contenders:
            try:
                self._leader = min(contenders, key=lambda broker: int(broker[-10:]))
                (identifier, _status) = self._zookeeper.get('/{}/{}'.format(self._contenders, self._leader))
                self._leader_identifier = identifier.decode('utf-8')
                return
            except NoNodeError:
                pass
            self._leader = None
            self._leader_identifier = None

    def leader(self):
        '''
        Get current leader
        '''
        return self._leader

    def identifier(self):
        '''
        Get current leader identifier
        '''
        return self._leader_identifier

if __name__ == '__main__':
    stopped = threading.Event()

    def handler(_signalnum, _frame):
        '''
        Signal handler
        '''
        stopped.set()

    signal.signal(signal.SIGINT, handler)

    watch = Watch('127.0.0.1', 2181, 'brokers')
    while not stopped.is_set():
        print(watch.identifier())
        time.sleep(1)

    stopped.wait()
