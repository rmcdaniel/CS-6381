'''
Publisher Module
'''
import zmq

from .directory import DirectoryClient
from .interfaces import Interfaces

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

    def publish(self, topic, message):
        '''
        Publish to a topic
        '''
        self._socket.send_string('{} {}'.format(topic, message))

    def start(self):
        '''
        Start the publisher
        '''
        if not self._started:
            self._started = True
            if self._relay:
                self._socket.connect('tcp://{}:{}'.format(self._address, self._port))
            else:
                address = Interfaces(self._stopped).address()
                port = self._socket.bind_to_random_port('tcp://*')
                DirectoryClient(self._address, self._port).register(address, port)
