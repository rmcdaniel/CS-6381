'''
Election Application
'''
import argparse
import signal
import threading

from election import Election

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

    election = Election('127.0.0.1', 2181, stopped)
    election.register('brokers', args.address, args.port)

    stopped.wait()
