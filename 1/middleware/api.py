'''
Api Module
'''
import signal
import threading
from .directory import Interfaces
from .services import broker_service
from .services import publisher_service
from .services import subscriber_service

class Api():
    '''
    Api Class
    '''
    def __init__(self, address, port, relay):
        '''
        Contstructor
        '''
        self.address = address
        self.port = port
        self.relay = relay
        self.publishers = []
        self.subscribers = []
        self.lock = threading.Lock()
        self.stopped = threading.Event()

        def handler(_signalnum, _frame):
            '''
            Signal handler
            '''
            self.stopped.set()

        signal.signal(signal.SIGINT, handler)

    def running(self):
        '''
        Check if we should stop running
        '''
        return not self.stopped.is_set()

    def broker(self):
        '''
        Broker service
        '''
        broker_service(self.address, self.port, self.relay, self.stopped)

    def register_pub(self):
        '''
        Register a publisher with the broker
        '''
        socket = publisher_service(self.address, self.port, self.relay, self.stopped)
        self.publishers.append(socket)

    def register_sub(self, topic):
        '''
        Register a subscriber with the broker
        '''
        buffer = []
        with self.lock:
            self.subscribers.append(buffer)

        def callback(string):
            '''
            Subscriber callback
            '''
            with self.lock:
                buffer.append(string)

        subscriber_service(self.address, self.port, self.relay, topic, callback, self.stopped)

    def notify(self, topic):
        '''
        Check a topic for new messages
        '''
        with self.lock:
            for subscriber_index, messages in enumerate(self.subscribers):
                if messages:
                    for message_index, message in enumerate(messages):
                        message_topic = message.split()
                        if topic == message_topic[0]:
                            value = message_topic[1:]
                            self.subscribers[subscriber_index].pop(message_index)
                            return value
        return None

    def publish(self, topic, value):
        '''
        Publish to a topic
        '''
        for publisher in self.publishers:
            publisher.send_string('{} {}'.format(topic, value))

    def ip(self):
        '''
        Get IP address
        '''
        return Interfaces(self.stopped).address()
