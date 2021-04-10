'''
Election Module
'''
from kazoo.client import KazooClient

class Election():
    '''
    Election Class
    '''
    def __init__(self, address, port, stopped):
        '''
        Constructor
        '''
        self._stopped = stopped

        self._identifier = None
        self._election = None

        self._zookeeper = KazooClient(hosts='{}:{}'.format(address, port))
        self._zookeeper.start()

    def register(self, contenders, address, port):
        '''
        Register a contender
        '''
        self._identifier = '{}:{}'.format(address, port)
        self._election = self._zookeeper.Election('/{}'.format(contenders), self._identifier)
        self._election.run(self.handle)

    def handle(self):
        '''
        Called when this contender becomes the leader
        '''
        self._stopped.wait()
