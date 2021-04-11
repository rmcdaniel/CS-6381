'''
Interfaces Module
'''
import array
import fcntl
import socket
import struct
import sys

class Interfaces():
    '''
    Network Interfaces Class
    '''
    def __init__(self, stopped):
        '''
        Constructor
        '''
        self._stopped = stopped

    def all(self):
        '''
        Get all network interfaces
        '''
        struct_size = 40 if (sys.maxsize > 2**32) else 32
        interface_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        max_number_of_structs = 8
        while not self._stopped.is_set():
            number_of_bytes = max_number_of_structs * struct_size
            interfaces_bytes = array.array('B')
            for i in range(0, number_of_bytes):
                interfaces_bytes.append(0)
            packed = struct.pack('iL', number_of_bytes, interfaces_bytes.buffer_info()[0])
            interface = fcntl.ioctl(interface_socket.fileno(), 0x8912, packed)
            unpacked = struct.unpack('iL', interface)[0]
            if unpacked == number_of_bytes:
                max_number_of_structs *= 2
            else:
                break
        if self._stopped.is_set():
            return []
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
