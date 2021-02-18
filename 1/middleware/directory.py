'''
Directory Module
'''
import json
import threading
import uuid
import zmq

class DirectoryClient():
    '''
    Directory Client Class
    '''
    def __init__(self, address, port):
        '''
        Constructor
        '''
        self.address = address
        self.port = port

    def register(self, address, port):
        '''
        Register a publisher
        '''
        context = zmq.Context()
        client_socket = context.socket(zmq.REQ)
        client_socket.connect('tcp://{}:{}'.format(self.address, self.port))
        client_socket.send_string('register {} {}'.format(address, port))
        client_socket.recv_string()
        client_socket.close()

    def list(self):
        '''
        Get list of publishers
        '''
        context = zmq.Context()
        client_socket = context.socket(zmq.REQ)
        client_socket.connect('tcp://{}:{}'.format(self.address, self.port))
        client_socket.send_string('list')
        string = client_socket.recv_string()
        client_socket.close()
        return dict(json.loads(string))

class DirectoryServer():
    '''
    Directory Class
    '''
    def __init__(self, address, port, stopped):
        '''
        Constructor
        '''
        self.address = address
        self.port = port
        self.stopped = stopped

    def start(self):
        '''
        Start directory server
        '''
        services = {}

        def server_thread():
            context = zmq.Context()
            socket = context.socket(zmq.REP)
            socket.bind('tcp://*:{}'.format(self.port))

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)

            while not self.stopped.is_set():
                sockets = dict(poller.poll(1000))
                if sockets.get(socket) == zmq.POLLIN:
                    data = socket.recv_string().split()
                    if data[0] == 'register':
                        services[uuid.uuid4().hex] = [data[1], data[2]]
                        socket.send_string('ok')
                    elif data[0] == 'list':
                        socket.send_string(json.dumps(services))
            socket.close()

        thread = threading.Thread(target=server_thread)
        thread.daemon = True
        thread.start()
