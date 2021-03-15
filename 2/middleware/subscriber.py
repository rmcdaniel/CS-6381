'''
Subscriber Module
'''
import threading
import time
import zmq

from .directory import DirectoryClient
from .watch import Watch

class Subscriber():
    '''
    Subscriber Class
    '''
    def __init__(self, address, port, relay, stopped):
        '''
        Constructor
        '''
        self._address = address
        self._port = port
        self._relay = relay
        self._stopped = stopped

        self._buffer = []
        self._lock = threading.Lock()
        self._started = False

        self._socket = zmq.Context().socket(zmq.SUB)
        self._watch = Watch(self._address, self._port, 'brokers')

    def connect(self, address, port):
        '''
        Connect to publisher
        '''
        self._socket.connect('tcp://{}:{}'.format(address, port))

    def subscribe(self, topic):
        '''
        Subscribe to topic
        '''
        self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def start(self):
        '''
        Start receiving messages
        '''
        def directory_thread():
            current_leader = None
            while not self._stopped.is_set():
                new_leader = self._watch.identifier()
                if current_leader != new_leader and not new_leader is None:
                    current_leader = new_leader
                    (broker_address, broker_port) = current_leader.split(':')
                    if self._relay:
                        self.connect(broker_address, int(broker_port) + 1)
                    else:
                        publishers = {}
                        client = DirectoryClient(broker_address, broker_port)
                        while not self._stopped.is_set() and current_leader == self._watch.identifier():
                            for publisher in client.list().items():
                                (identifier, (address, port)) = publisher
                                if not identifier in publishers:
                                    publishers[identifier] = [address, port]
                                    self.connect(address, port)
                            time.sleep(1)

        def subscriber_thread():
            poller = zmq.Poller()
            poller.register(self._socket, zmq.POLLIN)

            while not self._stopped.is_set():
                if dict(poller.poll(1000)).get(self._socket) == zmq.POLLIN:
                    with self._lock:
                        self._buffer.append(self._socket.recv_string())

        if not self._started:
            self._started = True
            thread = threading.Thread(target=directory_thread)
            thread.daemon = True
            thread.start()

            thread = threading.Thread(target=subscriber_thread)
            thread.daemon = True
            thread.start()

    def notify(self, topic):
        '''
        Check if topic has a message and return it
        '''
        with self._lock:
            for index, message in enumerate(self._buffer):
                message_topic = message.split()
                if topic == message_topic[0]:
                    message_body = message_topic[1:]
                    self._buffer.pop(index)
                    return message_body
        return None
