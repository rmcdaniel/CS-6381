'''
Proxy Module
'''
import threading
import zmq

class Proxy():
    '''
    Proxy Class
    '''
    def __init__(self):
        '''
        Constructor
        '''
        self._port = None

    def start(self):
        '''
        Start the proxy
        '''
        def proxy_thread():
            context = zmq.Context()
            xpub = context.socket(zmq.XPUB)
            xsub = context.socket(zmq.XSUB)
            self._port = xsub.bind_to_random_port('tcp://*')
            xpub.bind('tcp://*:{}'.format(self._port + 1))
            zmq.proxy(xsub, xpub)

        thread = threading.Thread(target=proxy_thread)
        thread.daemon = True
        thread.start()

    def port(self):
        '''
        Get proxy port
        '''
        return self._port
