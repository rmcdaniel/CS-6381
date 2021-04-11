import bisect
import hashlib

class Hash():
    def __init__(self, servers):
        self._servers = servers
        self._keys = []
        self._values = {}

    @staticmethod
    def hash(key):
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def hashes(self, key):
        return (Hash.hash('{}:{}'.format(key, i))
            for i in range(self._servers))

    def values(self):
        return self._values

    def __setitem__(self, key, value):
        for _hash in self.hashes(key):
            if _hash in self._values:
                raise ValueError('{} already exists'.format(key))
            self._values[_hash] = value
            bisect.insort(self._keys, _hash)

    def __delitem__(self, key):
        for _hash in self.hashes(key):
            del self._values[_hash]
            index = bisect.bisect_left(self._keys, _hash)
            del self._keys[index]

    def __getitem__(self, key):
        _hash = Hash.hash(key)
        start = bisect.bisect(self._keys, _hash)
        if start == len(self._keys):
            start = 0
        return self._values[self._keys[start]]
