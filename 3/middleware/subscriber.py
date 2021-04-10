'''
Subscriber Module
'''
import threading
import zmq

from .election import Election
from .interfaces import Interfaces
from .watch import Watch

class Subscriber():
    '''
    Subscriber Class
    '''
    def __init__(self, address, port, stopped):
        '''
        Constructor
        '''
        self._address = address
        self._port = port
        self._stopped = stopped

        self._buffer = []
        self._election = None
        self._lock = threading.Lock()
        self._started = False

        self._socket = zmq.Context().socket(zmq.SUB)
        self._watch = Watch(self._address, self._port)

    def subscribe(self, topic):
        '''
        Subscribe to topic
        '''
        self._socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def start(self):
        '''
        Start receiving messages
        '''
        def election_thread():
            self._election = Election(self._address, self._port, self._stopped)
            self._election.register('subscribers', '', '')

        def watch_thread():
            current_broker = None
            while not self._stopped.is_set():
                new_broker = self._watch.identifier(Interfaces(self._stopped).address())
                if current_broker != new_broker and not new_broker is None:
                    if not current_broker is None:
                        (address, port) = current_broker.split(':')
                        self._socket.disconnect('tcp://{}:{}'.format(address, int(port) + 1))
                    current_broker = new_broker
                    (address, port) = current_broker.split(':')
                    self._socket.connect('tcp://{}:{}'.format(address, int(port) + 1))

        def subscriber_thread():
            poller = zmq.Poller()
            poller.register(self._socket, zmq.POLLIN)

            while not self._stopped.is_set():
                if dict(poller.poll(1000)).get(self._socket) == zmq.POLLIN:
                    with self._lock:
                        self._buffer.append(self._socket.recv_string())

        if not self._started:
            self._started = True
            thread = threading.Thread(target=election_thread)
            thread.daemon = True
            thread.start()

            thread = threading.Thread(target=watch_thread)
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