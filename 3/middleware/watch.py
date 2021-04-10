'''
Election Application
'''
from .hash import Hash
from kazoo.client import KazooClient
from kazoo.exceptions import NoNodeError

class Watch():
    '''
    Watch class
    '''
    def __init__(self, address, port, brokers='brokers', subscribers='subscribers'):
        '''
        Constructor
        '''
        self._brokers = brokers
        self._subscribers = subscribers
        self._threshold = 1

        self._hash = None

        self._zookeeper = KazooClient(hosts='{}:{}'.format(address, port))
        self._zookeeper.start()
        self._zookeeper.ChildrenWatch('/{}'.format(brokers), self.watch)
        self._zookeeper.ChildrenWatch('/{}'.format(subscribers), self.watch)

    def watch(self, _nodes):
        '''
        Called when a directory changes
        '''
        try:
            brokers = self._zookeeper.get_children('/{}'.format(self._brokers))
        except NoNodeError:
            brokers = None
        if brokers:
            count = (len(self._zookeeper.get_children('/{}'.format(self._subscribers))) // self._threshold) + 1
            brokers.sort(key=lambda broker: int(broker[-10:]))
            brokers = brokers[:count]
            self._hash = Hash(len(brokers))
            for broker in brokers:
                try:
                    (identifier, _status) = self._zookeeper.get('/{}/{}'.format(self._brokers, broker))
                    self._hash[broker] = identifier
                except NoNodeError:
                    pass

    def all(self):
        '''
        Get all identifiers
        '''
        if self._hash and len(self._hash.values()) != 0:
            return list(map(lambda value: value.decode('utf-8'), self._hash.values().values()))
        return {}

    def identifier(self, key):
        '''
        Get identifier for key
        '''
        if self._hash and len(self._hash.values()) != 0:
            return self._hash[key].decode('utf-8')
        return None
