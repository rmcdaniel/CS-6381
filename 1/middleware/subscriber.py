'''
Subscriber Module
'''
import threading
import zmq

class Subscriber():
    '''
    Subscriber Class
    '''
    def __init__(self, address, port, topic, callback, stopped):
        '''
        Constructor
        '''
        self.address = address
        self.port = port
        self.topic = topic
        self.callback = callback
        self.stopped = stopped

    def start(self):
        '''
        Start the subscriber
        '''
        def subscriber_thread(thread_socket):
            thread_socket.setsockopt_string(zmq.SUBSCRIBE, self.topic)
            while not self.stopped.is_set():
                string = thread_socket.recv_string()
                self.callback(string)

        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        socket.connect('tcp://{}:{}'.format(self.address, self.port))

        thread = threading.Thread(target=subscriber_thread, args=(socket, ))
        thread.daemon = True
        thread.start()
