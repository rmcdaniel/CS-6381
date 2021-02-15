'''
Services Module
'''
import threading
import time

from middleware import directory
from middleware import proxy
from middleware import publisher
from middleware import subscriber

def broker_service(address, port, relay, stopped):
    '''
    Run broker
    '''
    if relay:
        proxy_server = proxy.Proxy(address, port)
        proxy_server.start()
    else:
        directory_server = directory.DirectoryServer(address, port, stopped)
        directory_server.start()
    stopped.wait()

def publisher_service(address, port, relay):
    '''
    Run publisher
    '''
    publisher_server = publisher.Publisher(address, port, relay)
    (socket, publisher_port) = publisher_server.start()
    if not relay:
        directory_client = directory.DirectoryClient(address, port)
        directory_client.register(address, publisher_port)
    return socket

def subscriber_service(address, port, relay, topic, callback, stopped):
    '''
    Run subscriber
    '''
    def subscriber_thread(address, port, relay, topic, callback, stopped):
        if relay:
            subscriber_client = subscriber.Subscriber(address, port + 1, topic, callback, stopped)
            subscriber_client.start()
        else:
            publishers_list = {}
            while not stopped.is_set():
                directory_client = directory.DirectoryClient(address, port)
                publishers = directory_client.list()
                for item in publishers.items():
                    (identifier, (address, publisher_port)) = item
                    if not identifier in publishers_list:
                        publishers_list[identifier] = [address, publisher_port]
                        subscriber_client = subscriber.Subscriber(address, publisher_port, topic, callback, stopped)
                        subscriber_client.start()
            time.sleep(1)

    thread = threading.Thread(target=subscriber_thread, args=(address, port, relay, topic, callback, stopped))
    thread.daemon = True
    thread.start()
