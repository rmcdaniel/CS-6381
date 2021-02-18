'''
Api Module
'''
import signal
import threading

from .directory import DirectoryClient, DirectoryServer
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
        self._proxy = None
        self._publisher = None
        self._subscriber = None

        def handler(_signalnum, _frame):
            '''
            Signal handler
            '''
            self._stopped.set()

        signal.signal(signal.SIGINT, handler)

        self._directory = None
        self._proxy = None

    def running(self):
        '''
        Check if we should stop running
        '''
        return not self._stopped.is_set()

    def broker(self):
        '''
        Broker service
        '''
        if self._relay:
            if not self._proxy:
                self._proxy = Proxy(self._address, self._port)
                self._proxy.start()
        else:
            if not self._directory:
                self._directory = DirectoryServer(self._address, self._port, self._stopped)
                self._directory.start()
        self._stopped.wait()

    def publisher(self):
        '''
        Register a publisher with the broker
        '''
        self._publisher = Publisher(self._relay, self._stopped)
        if self._relay:
            pass
        else:
            self._publisher.start(self._address, self._port)

    def subscriber(self, topic):
        '''
        Register a subscriber with the broker
        '''
        self._subscriber = Subscriber(self._stopped)
        self._subscriber.subscribe(topic)
        self._subscriber.start()
        self._subscriber.connect(self._address, self._port)

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

    def ip(self):
        '''
        Get IP address
        '''
        return Interfaces(self._stopped).address()
