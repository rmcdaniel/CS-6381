'''
Subscriber Module
'''
import threading
import zmq

class Subscriber():
    '''
    Subscriber Class
    '''
    def __init__(self, stopped):
        '''
        Constructor
        '''
        self.stopped = stopped

        self.buffer = []
        self.lock = threading.Lock()
        self.started = False

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.SUB)

    def connect(self, address, port):
        '''
        Connect to publisher
        '''
        self.socket.connect('tcp://{}:{}'.format(address, port))

    def subscribe(self, topic):
        '''
        Subscribe to topic
        '''
        self.socket.setsockopt_string(zmq.SUBSCRIBE, topic)

    def start(self):
        '''
        Start receiving messages
        '''
        def subscriber_thread():
            poller = zmq.Poller()
            poller.register(self.socket, zmq.POLLIN)

            while not self.stopped.is_set():
                if dict(poller.poll(1000)).get(self.socket) == zmq.POLLIN:
                    with self.lock:
                        self.buffer.append(self.socket.recv_string())

        if not self.started:
            thread = threading.Thread(target=subscriber_thread)
            thread.daemon = True
            thread.start()

    def notify(self, topic):
        '''
        Check if topic has a message and return it
        '''
        with self.lock:
            for index, message in enumerate(self.buffer):
                message_topic = message.split()
                if topic == message_topic[0]:
                    message_body = message_topic[1:]
                    self.buffer.pop(index)
                    return message_body
        return None
