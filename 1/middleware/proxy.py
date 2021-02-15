'''
Proxy Module
'''
import threading
import zmq

class Proxy():
    '''
    Proxy Class
    '''
    def __init__(self, address, port):
        '''
        Constructor
        '''
        self.address = address
        self.port = port

    def start(self):
        '''
        Start the proxy
        '''
        def proxy_thread():
            context = zmq.Context()
            xpub = context.socket(zmq.XPUB)
            xsub = context.socket(zmq.XSUB)
            xsub.bind('tcp://*:{}'.format(self.port))
            xpub.bind('tcp://*:{}'.format(self.port + 1))
            zmq.proxy(xsub, xpub)

        thread = threading.Thread(target=proxy_thread)
        thread.daemon = True
        thread.start()
