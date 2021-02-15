'''
Directory Module
'''
import json
import socket
import threading
import uuid

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
        client = socket.socket()
        client.connect((self.address, self.port))
        client.sendall('register {} {}'.format(address, port).encode('utf-8'))

    def list(self):
        '''
        Get list of publishers
        '''
        client = socket.socket()
        client.connect((self.address, self.port))
        client.sendall('list'.encode('utf-8'))
        return dict(json.loads(client.recv(1024).decode('utf-8')))

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
        lock = threading.Lock()
        services = {}

        def client_thread(client):
            while not self.stopped.is_set():
                try:
                    data = client.recv(1024).decode('utf-8')
                    if not data:
                        break
                    data = data.split()
                    if data[0] == 'register':
                        with lock:
                            services[uuid.uuid4().hex] = [data[1], data[2]]
                    elif data[0] == 'list':
                        with lock:
                            client.sendall(json.dumps(services).encode('utf-8'))
                except OSError:
                    pass
            try:
                client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client.close()

        def server_thread():
            server = socket.socket()
            server.setblocking(0)
            server.bind(('0.0.0.0', self.port))
            server.listen()
            while not self.stopped.is_set():
                try:
                    client, _address = server.accept()
                    client.setblocking(0)
                    thread = threading.Thread(target=client_thread, args=(client, ))
                    thread.start()
                except OSError:
                    pass
            try:
                server.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            server.close()

        thread = threading.Thread(target=server_thread)
        thread.daemon = True
        thread.start()
