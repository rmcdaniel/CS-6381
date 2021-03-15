'''
Api Module
'''
import signal
import threading

from .directory import DirectoryServer
from .election import Election
from .interfaces import Interfaces
from .proxy import Proxy
from .publisher import Publisher
from .subscriber import Subscriber

class Api():
    '''
    Api Class
    '''
    def __init__(self, address, port, relay):
        '''
        Contstructor
        '''
        self._address = address
        self._port = port
        self._relay = relay
        self._stopped = threading.Event()

        self._directory = None
        self._election = None
        self._proxy = None
        self._publisher = None
        self._subscriber = None

        def handler(_signalnum, _frame):
            '''
            Signal handler
            '''
            self._stopped.set()

        signal.signal(signal.SIGINT, handler)

    def running(self):
        '''
        Check if we should stop running
        '''
        return not self._stopped.is_set()

    def broker(self):
        '''
        Broker service
        '''
        self._election = Election(self._address, self._port, self._stopped)
        if self._relay:
            if not self._proxy:
                self._proxy = Proxy()
                self._proxy.start()
                self._election.register('brokers', self.address(), self._proxy.port())
        else:
            if not self._directory:
                self._directory = DirectoryServer(self._stopped)
                self._directory.start()
                self._election.register('brokers', self.address(), self._directory.port())

    def publisher(self):
        '''
        Register a publisher with the broker
        '''
        if not self._publisher:
            self._publisher = Publisher(self._address, self._port, self._relay, self._stopped)
            self._publisher.start()

    def subscriber(self, topic):
        '''
        Register a subscriber with the broker
        '''
        if not self._subscriber:
            self._subscriber = Subscriber(self._address, self._port, self._relay, self._stopped)
            self._subscriber.start()
        self._subscriber.subscribe(topic)

    def notify(self, topic):
        '''
        Check a topic for new messages
        '''
        return self._subscriber.notify(topic)

    def publish(self, topic, message):
        '''
        Publish to a topic
        '''
        self._publisher.publish(topic, message)

    def address(self):
        '''
        Get IP address
        '''
        return Interfaces(self._stopped).address()
