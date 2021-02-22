'''
Election Application
'''
import signal
import threading
from kazoo.client import KazooClient

def leader(brokers):
    '''
    Called when tne brokers change
    '''
    print(brokers)
    if len(brokers):
        print('looks like we got a new captian')
        (address, status) = zk.get('/brokers/{}'.format(brokers[0]))
        print(address, status)
    else:
        print('abandon ship')

if __name__ == '__main__':
    stopped = threading.Event()

    def handler(_signalnum, _frame):
        '''
        Signal handler
        '''
        stopped.set()

    signal.signal(signal.SIGINT, handler)

    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()
    watcher = zk.ChildrenWatch('/brokers', leader)
    stopped.wait()
