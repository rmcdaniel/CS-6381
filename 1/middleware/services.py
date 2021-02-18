'''
Services Module
'''
import threading
import time
import zmq

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

def subscriber_service(address, port, relay, topics, stopped, callback):
    '''
    Run subscriber
    '''
    def subscriber_thread():
        last_directory_query = 0
        publishers_list = {}
        subscriber_sockets = []
        poller = zmq.Poller()
        subscribed_topics = []

        while not stopped.is_set():
            if relay:
                try:
                    topic = topics.get(False)
                except queue.Empty:
                    topic = None
                if topic:
                    subscribed_topics = 
                    subscriber_client = subscriber.Subscriber(address, port + 1, topic, stopped)
                    subscriber_socket = subscriber_client.start()
                    subscriber_sockets.append(subscriber_socket)
                    poller.register(subscriber_socket, zmq.POLLIN)
            else:
                if time.time() - last_directory_query >= 1:
                    last_directory_query = time.time()
                    directory_client = directory.DirectoryClient(address, port)
                    publishers = directory_client.list()
                    for publisher_item in publishers.items():
                        (publisher_identifier, (publisher_address, publisher_port)) = publisher_item
                        if not publisher_identifier in publishers_list:
                            publishers_list[publisher_identifier] = [publisher_address, publisher_port]
                            subscriber_client = subscriber.Subscriber(publisher_address, publisher_port, topic, stopped)
                            subscriber_socket = subscriber_client.start()
                            subscriber_sockets.append(subscriber_socket)
                            poller.register(subscriber_socket, zmq.POLLIN)

            sockets = dict(poller.poll(1000))
            for subscriber_socket in subscriber_sockets:
                if sockets.get(subscriber_socket) == zmq.POLLIN:
                    callback(subscriber_socket.recv_string())

    thread = threading.Thread(target=subscriber_thread)
    thread.daemon = True
    thread.start()
