import time

class Cache():
    def __init__(self):
        self._keys = []
        self._items = {}

    def __setitem__(self, key, value):
        self._items[key] = {
            'expiration': time.time() + 5,
            'value': value,
        }

    def __delitem__(self, key):
        del self._items[key]

    def __getitem__(self, key):
        item = self._items[key]
        if item['expiration'] < time.time():
            del self._items[key]
            raise KeyError(key)
        return item['value']
