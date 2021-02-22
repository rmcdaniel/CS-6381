'''
Election Application
'''
import argparse
import signal
import threading

from kazoo.client import KazooClient

class Election():

    def __init__(self, address, port):
        self.zk = KazooClient(hosts='{}:{}'.format(address, port))
        self.zk.start()

    def register(self, address, port):
        election = self.zk.Election('/brokers', '{}:{}'.format(address, port))
        election.run(self.handle)

    def handle(self):
        '''
        Called when this broker becomes the leader
        '''
        print('look at me, I am the captain now')

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

    election = Election('127.0.0.1', 2181)
    election.register(args.address, args.port)

    stopped.wait()
