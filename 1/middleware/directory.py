'''
Directory Module
'''
import array
import fcntl
import json
import socket
import struct
import sys
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
        try:
            client = socket.socket()
            client.connect((self.address, self.port))
            client.sendall('register {} {}'.format(address, port).encode('utf-8'))
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except OSError:
            pass

    def list(self):
        '''
        Get list of publishers
        '''
        try:
            client = socket.socket()
            client.connect((self.address, self.port))
            client.sendall('list'.encode('utf-8'))
            try:
                publishers = dict(json.loads(client.recv(1024).decode('utf-8')))
            except json.JSONDecodeError:
                publishers = {}
            client.shutdown(socket.SHUT_RDWR)
            client.close()
        except OSError:
            publishers = {}
        return publishers

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
            server.listen(1024)
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

class Interfaces():
    '''
    Network Interfaces Class
    '''
    def __init__(self, stopped):
        '''
        Constructor
        '''
        self.stopped = stopped

    def all(self):
        '''
        Get all network interfaces
        '''
        SIOCGIFCONF = 0x8912
        struct_size = 40 if (sys.maxsize > 2**32) else 32
        interface_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        max_number_of_structs = 8
        while not self.stopped.is_set():
            number_of_bytes = max_number_of_structs * struct_size
            interfaces_bytes = array.array('B')
            for i in range(0, number_of_bytes):
                interfaces_bytes.append(0)
            packed = struct.pack('iL', number_of_bytes, interfaces_bytes.buffer_info()[0])
            interface = fcntl.ioctl(interface_socket.fileno(), SIOCGIFCONF, packed)
            unpacked = struct.unpack('iL', interface)[0]
            if unpacked == number_of_bytes:
                max_number_of_structs *= 2
            else:
                break
        interfaces_strings = interfaces_bytes.tostring()
        interfaces = []
        for i in range(0, unpacked, struct_size):
            name = bytes.decode(interfaces_strings[i:i + 16]).split('\0', 1)[0]
            address = socket.inet_ntoa(interfaces_strings[i + 20:i + 24])
            interfaces.append({'name': name, 'address': address})

        return interfaces

    def address(self):
        '''
        Return first non loopback interface address
        '''
        interfaces = self.all()
        interfaces = [interface for interface in interfaces if interface['name'] != 'lo']
        return interfaces.pop()['address']
