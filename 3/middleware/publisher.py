'''
Publisher Module
'''
import threading
import zmq

from .interfaces import Interfaces
from .watch import Watch

class Publisher():
    '''
    Publisher Class
    '''
    def __init__(self, address, port, stopped):
        '''
        Constructor
        '''
        self._address = address
        self._port = port
        self._stopped = stopped

        self._history = {}
        self._started = False

        self._socket = zmq.Context().socket(zmq.PUB)
        self._watch = Watch(self._address, self._port)

    def publish(self, topic, ownership, message, history):
        '''
        Publish to a topic
        '''
        try:
            messages = self._history[topic]
        except KeyError:
            messages = []
        if len(messages) >= history:
            messages.pop(0)
        messages.append(message)
        self._history[topic] = messages
        for saved_message in messages:
            self._socket.send_string('{} {} {}'.format(topic, ownership, saved_message))

    def start(self):
        '''
        Start the publisher
        '''
        def publisher_thread():
            current_brokers = None
            while not self._stopped.is_set():
                new_brokers = self._watch.all()
                if current_brokers != new_brokers and not new_brokers is None:
                    if not current_brokers is None:
                        for broker in current_brokers:
                            if not broker in new_brokers:
                                (address, port) = broker.split(':')
                                try:
                                    self._socket.disconnect('tcp://{}:{}'.format(address, int(port) + 1))
                                except zmq.error.ZMQError:
                                    pass
                    current_brokers = new_brokers
                    for broker in current_brokers:
                        (address, port) = broker.split(':')
                        self._socket.connect('tcp://{}:{}'.format(address, port))

        if not self._started:
            self._started = True
            thread = threading.Thread(target=publisher_thread)
            thread.daemon = True
            thread.start()
