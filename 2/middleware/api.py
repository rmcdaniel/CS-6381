'''
Api Module
'''
import signal
import threading

from .directory import DirectoryServer
from .interfaces import Interfaces
from .proxy import Proxy
from .publisher import Publisher
from .subscriber import Subscriber

from ..zk_ware.election import Election
from ..zk_ware.watch import Watch

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

    def running(self):
        '''
        Check if we should stop running
        '''
        return not self._stopped.is_set()

    def broker(self):
        '''
        Broker service
        '''
        election = Election('127.0.0.1', 2181, self._stopped)
        election.register('brokers', self._address, self._port)
        
        if self._relay:
            if not self._proxy:
                self._proxy = Proxy(self._port)
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
        if not self._publisher:
            watch = Watch('127.0.0.1', 2181, 'brokers')
            current_leader = watch.leader().split(":")
            self._publisher = Publisher(current_leader[0], current_leader[1], self._relay, self._stopped)
            self._publisher.start()

            while not self._stopped.is_set():
                new_leader = watch.leader()
                if new_leader != None and new_leader != current_leader:
                    current_leader = new_leader
                    self._publisher.stop()
                    self._publisher = Publisher(current_leader[0], current_leader[1], self._relay, self._stopped)
                    self._publisher.start()

    def subscriber(self, topic):
        '''
        Register a subscriber with the broker
        '''
        if not self._subscriber:
            watch = Watch('127.0.0.1', 2181, 'brokers')
            current_leader = watch.leader().split(":")
            self._subscriber = Subscriber(current_leader[0], current_leader[1], self._relay, self._stopped)
            self._subscriber.start()

            while not self._stopped.is_set():
                new_leader = watch.leader()
                if new_leader != None and new_leader != current_leader:
                    current_leader = new_leader
                    self._subscriber.stop()
                    self._subscriber = Subscriber(current_leader[0], current_leader[1], self._relay, self._stopped)
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
