'''
Publisher Module
'''
import zmq

class Publisher():
    '''
    Publisher Class
    '''
    def __init__(self, relay, stopped):
        '''
        Constructor
        '''
        self.relay = relay
        self.stopped = stopped

        self.port = None
        self.started = False

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)

    def publish(self, topic, message):
        '''
        Publish to a topic
        '''
        self.socket.send_string('{} {}'.format(topic, message))

    def start(self, address=None, port=None):
        '''
        Start the publisher
        '''
        if not self.started:
            if self.relay:
                self.socket.connect('tcp://{}:{}'.format(address, port))
            else:
                self.socket.bind('tcp://{}:{}'.format(address, port))
                # self.port = self.socket.bind_to_random_port('tcp://*')
