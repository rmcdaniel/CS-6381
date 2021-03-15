'''
Publisher Module
'''
import threading
import zmq

from .directory import DirectoryClient
from .interfaces import Interfaces
from .watch import Watch

class Publisher():
    '''
    Publisher Class
    '''
    def __init__(self, address, port, relay, stopped):
        '''
        Constructor
        '''
        self._address = address
        self._port = port
        self._relay = relay
        self._stopped = stopped

        self._started = False

        self._socket = zmq.Context().socket(zmq.PUB)
        self._watch = Watch(self._address, self._port, 'brokers')

    def publish(self, topic, message):
        '''
        Publish to a topic
        '''
        self._socket.send_string('{} {}'.format(topic, message))

    def start(self):
        '''
        Start the publisher
        '''
        def publisher_thread(address, port):
            current_leader = None
            while not self._stopped.is_set():
                new_leader = self._watch.identifier()
                if current_leader != new_leader and not new_leader is None:
                    current_leader = new_leader
                    (broker_address, broker_port) = current_leader.split(':')
                    if self._relay:
                        self._socket.connect('tcp://{}:{}'.format(broker_address, broker_port))
                    else:
                        DirectoryClient(broker_address, broker_port).register(address, port)

        if not self._started:
            self._started = True
            if self._relay:
                address = None
                port = None
            else:
                address = Interfaces(self._stopped).address()
                port = self._socket.bind_to_random_port('tcp://*')
            thread = threading.Thread(target=publisher_thread, args=(address, port, ))
            thread.daemon = True
            thread.start()
