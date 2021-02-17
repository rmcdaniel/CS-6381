'''
Subscriber Module
'''
import zmq

class Subscriber():
    '''
    Subscriber Class
    '''
    def __init__(self, address, port, topic, stopped):
        '''
        Constructor
        '''
        self.address = address
        self.port = port
        self.topic = topic
        self.stopped = stopped

    def start(self):
        '''
        Start the subscriber
        '''
        context = zmq.Context()
        subscriber_socket = context.socket(zmq.SUB)
        subscriber_socket.connect('tcp://{}:{}'.format(self.address, self.port))
        subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
        return subscriber_socket
