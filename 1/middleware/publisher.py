'''
Publisher Module
'''
import zmq

class Publisher():
    '''
    Publisher Class
    '''
    def __init__(self, address, port, relay):
        '''
        Constructor
        '''
        self.address = address
        self.port = port
        self.relay = relay

    def start(self):
        '''
        Start the publisher
        '''
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        if self.relay:
            port = None
            socket.connect('tcp://{}:{}'.format(self.address, self.port))
        else:
            port = socket.bind_to_random_port('tcp://*')
        return (socket, port)
