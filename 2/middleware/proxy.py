'''
Proxy Module
'''
import threading
import zmq

class Proxy():
    '''
    Proxy Class
    '''
    def __init__(self, port):
        '''
        Constructor
        '''
        self._port = port

    def start(self):
        '''
        Start the proxy
        '''
        def proxy_thread():
            context = zmq.Context()
            xpub = context.socket(zmq.XPUB)
            xsub = context.socket(zmq.XSUB)
            xsub.bind('tcp://*:{}'.format(self._port))
            xpub.bind('tcp://*:{}'.format(self._port + 1))
            zmq.proxy(xsub, xpub)

        thread = threading.Thread(target=proxy_thread)
        thread.daemon = True
        thread.start()
