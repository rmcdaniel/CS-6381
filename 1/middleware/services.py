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

def publisher_service(address, port, relay, stopped):
    '''
    Run publisher
    '''
    publisher_server = publisher.Publisher(address, port, relay)
    (socket, publisher_port) = publisher_server.start()
    if not relay:
        publisher_address = directory.Interfaces(stopped).address()
        directory_client = directory.DirectoryClient(address, port)
        directory_client.register(publisher_address, publisher_port)
    return socket

def subscriber_service(address, port, relay, topic, callback, stopped):
    '''
    Run subscriber
    '''
    def subscriber_thread(thread_address, thread_port, thread_relay, thread_topic, thread_callback, thread_stopped):
        if thread_relay:
            subscriber_client = subscriber.Subscriber(thread_address, thread_port + 1, thread_topic, thread_callback, thread_stopped)
            subscriber_client.start()
        else:
            publishers_list = {}
            while not thread_stopped.is_set():
                directory_client = directory.DirectoryClient(thread_address, thread_port)
                publishers = directory_client.list()
                for item in publishers.items():
                    (publisher_identifier, (publisher_address, publisher_port)) = item
                    if not publisher_identifier in publishers_list:
                        publishers_list[publisher_identifier] = [publisher_address, publisher_port]
                        subscriber_client = subscriber.Subscriber(publisher_address, publisher_port, thread_topic, thread_callback, thread_stopped)
                        subscriber_client.start()
                time.sleep(1)

    thread = threading.Thread(target=subscriber_thread, args=(address, port, relay, topic, callback, stopped))
    thread.daemon = True
    thread.start()
