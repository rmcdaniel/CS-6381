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
            server_socket = context.socket(zmq.REP)
            server_socket.bind('tcp://*:{}'.format(self.port))

            poller = zmq.Poller()
            poller.register(server_socket, zmq.POLLIN)

            while not self.stopped.is_set():
                sockets = dict(poller.poll(1000))
                if sockets.get(server_socket) == zmq.POLLIN:
                    data = server_socket.recv_string().split()
                    if data[0] == 'register':
                        services[uuid.uuid4().hex] = [data[1], data[2]]
                        server_socket.send_string('ok')
                    elif data[0] == 'list':
                        server_socket.send_string(json.dumps(services))
            server_socket.close()

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
