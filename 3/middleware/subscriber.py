'''
Subscriber Module
'''
import threading
import time
import zmq

from .cache import Cache
from .election import Election
from .hash import Hash
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
        self._cache = Cache()
        self._election = None
        self._history = []
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

    def notify(self, topic, history=2):
        '''
        Check if topic has a message and return it
        '''
        with self._lock:
            topics = {}
            for index, message in enumerate(self._buffer[:]):
                message_topic = message.split()
                try:
                    message_count = topics[message_topic[0]]
                except KeyError:
                    message_count = 0
                message_count += 1
                topics[message_topic[0]] = message_count
            offset = 0
            for index, message in enumerate(self._buffer[:]):
                message_topic = message.split()
                try:
                    message_count = topics[message_topic[0]]
                except KeyError:
                    message_count = 0
                if message_count > history:
                    self._buffer.pop(index - offset)
                    offset += 1
                    message_count -= 1
                topics[message_topic[0]] = message_count
            offset = 0
            for index, message in enumerate(self._buffer[:]):
                message_topic = message.split()
                if topic == message_topic[0]:
                    ownership = message_topic[1:2]
                    try:
                        cached = self._cache[topic]
                    except KeyError:
                        self._cache[topic] = ownership
                        cached = self._cache[topic]
                    message_body = message_topic[1:]
                    self._buffer.pop(index - offset)
                    offset += 1
                    if ownership >= cached:
                        self._cache[topic] = ownership
                        md5 = Hash.hash(message)
                        if not md5 in self._history:
                            self._history.append(md5)
                            return message_body
        return None
