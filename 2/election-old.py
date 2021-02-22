'''
Election Application
'''
import argparse
import signal
import threading

from kazoo.client import KazooClient

def broker():
    '''
    Called when this broker becomes the leader
    '''
    print('look at me, I am the captain now')
    stopped.wait()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Single Broker-Based Publish-Subscribe Using ZMQ')
    parser.add_argument('address', help='broker address')
    parser.add_argument('port', type=int, help='broker port')
    args = parser.parse_args()

    stopped = threading.Event()

    def handler(_signalnum, _frame):
        '''
        Signal handler
        '''
        stopped.set()

    signal.signal(signal.SIGINT, handler)

    zk = KazooClient(hosts='127.0.0.1:2181')
    zk.start()
    election = zk.Election('/brokers', '{}:{}'.format(args.address, args.port))
    election.run(broker)
