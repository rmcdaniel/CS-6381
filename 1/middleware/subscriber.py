'''
Subscriber Module
'''
import threading
import time
import zmq

from .directory import DirectoryClient

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
        def directoy_thread():
            if self._relay:
                self.connect(self._address, self._port + 1)
            else:
                publishers = {}
                client = DirectoryClient(self._address, self._port)
                while not self._stopped:
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
            thread = threading.Thread(target=directoy_thread)
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
