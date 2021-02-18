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
        self._address = address
        self._port = port

    def register(self, address, port):
        '''
        Register a publisher
        '''
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://{}:{}'.format(self._address, self._port))
        socket.send_string('register {} {}'.format(address, port))
        socket.recv_string()
        socket.close()

    def list(self):
        '''
        Get list of publishers
        '''
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect('tcp://{}:{}'.format(self._address, self._port))
        socket.send_string('list')
        string = socket.recv_string()
        socket.close()
        return dict(json.loads(string))

class DirectoryServer():
    '''
    Directory Class
    '''
    def __init__(self, address, port, stopped):
        '''
        Constructor
        '''
        self._address = address
        self._port = port
        self._stopped = stopped

    def start(self):
        '''
        Start directory server
        '''
        services = {}

        def server_thread():
            context = zmq.Context()
            socket = context.socket(zmq.REP)
            socket.bind('tcp://*:{}'.format(self._port))

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)

            while not self._stopped.is_set():
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
