'''
Main application
'''
import argparse
import random
import time

import middleware

def broker(options):
    '''
    Run broker
    '''
    api = middleware.Api(options.address, options.port, options.relay)
    api.broker()

def publisher(options):
    '''
    Run publisher
    '''
    api = middleware.Api(options.address, options.port, options.relay)
    api.publisher()
    address = api.address()
    sequence = 0
    while api.running():
        for topic_number in range(options.topics):
            api.publish('{}-topic'.format(topic_number), '{} {} {} {}'.format(address, sequence, random.random(), time.time_ns()))
            sequence += 1
        time.sleep(options.delay)

def subscriber(options):
    '''
    Run subscriber
    '''
    api = middleware.Api(options.address, options.port, options.relay)
    for topic_number in range(options.topics):
        api.subscriber('{}-topic'.format(topic_number))
    while api.running():
        for topic_number in range(options.topics):
            data = api.notify('{}-topic'.format(topic_number))
            if data:
                (address, sequence, value, nanoseconds) = data
                print(topic_number, address, sequence, value, (time.time_ns() - float(nanoseconds)) / 1e9)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Single Broker-Based Publish-Subscribe Using ZMQ')
    subparsers = parser.add_subparsers(dest='service', required=True, help='service to run')

    broker_parser = subparsers.add_parser('broker', help='broker options')
    broker_parser.add_argument('-r', '--relay', action='store_true', required=False, help='enable relay')
    broker_parser.add_argument('address', help='zookeeper address')
    broker_parser.add_argument('port', type=int, help='zookeeper port')

    publisher_parser = subparsers.add_parser('publisher', help='publisher options')
    publisher_parser.add_argument('-d', '--delay', type=float, default=1, required=False, help='time to wait between sends')
    publisher_parser.add_argument('-r', '--relay', action='store_true', required=False, help='use relay')
    publisher_parser.add_argument('-t', '--topics', type=int, default=1, required=False, help='number of topics')
    publisher_parser.add_argument('address', help='zookeeper address')
    publisher_parser.add_argument('port', type=int, help='zookeeper port')

    subscriber_parser = subparsers.add_parser('subscriber', help='subscriber options')
    subscriber_parser.add_argument('-r', '--relay', action='store_true', required=False, help='use relay')
    subscriber_parser.add_argument('-t', '--topics', type=int, default=1, required=False, help='number of topics')
    subscriber_parser.add_argument('address', help='zookeeper address')
    subscriber_parser.add_argument('port', type=int, help='zookeeper port')

    args = parser.parse_args()

    services_list = {
        'broker' : broker,
        'publisher' : publisher,
        'subscriber' : subscriber,
    }

    services_list[args.service](args)
