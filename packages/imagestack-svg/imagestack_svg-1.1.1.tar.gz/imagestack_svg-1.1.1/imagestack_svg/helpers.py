import asyncio
import re
from collections.abc import MutableMapping

def http_emoji_encode(c: str) -> str:
    return ''.join(['%' + hex(s)[2:].upper() for s in c.encode('utf-8')])

def from_char(c: str) -> str:
    return c.encode('utf-8').hex()


def to_char(c: str) -> str:
    return bytes.fromhex(c).decode('utf-8')


def is_emoji(emoji: str) -> bool:
    if len(emoji) != 1:
        return False
    regex_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002500-\U00002BEF"
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", re.UNICODE)
    return bool(regex_pattern.search(emoji))


class AsyncEvent(asyncio.Event):
    def set(self):
        # TODO: _loop is not documented
        self._loop.call_soon_threadsafe(super().set)


class CacheDict(MutableMapping):
    def __init__(self, max_size: int = 1):
        self.d = dict()
        self.uses = dict()
        self.max_size = max_size

    def clear(self) -> None:
        self.d.clear()
        self.uses.clear()

    def __getitem__(self, key):
        if self.max_size < 1:
            return self.d[key]
        self.uses[key] += 1
        return self.d[key]

    def __setitem__(self, key, value):
        if self.max_size < 1:
            return
        if self.__len__() >= self.max_size:
            self.__delitem__(min(self.uses.items(), key=lambda x: x[1])[0])
        self.uses[key] = 1
        self.d[key] = value

    def __delitem__(self, key):
        del self.uses[key]
        del self.d[key]

    def __iter__(self):
        return iter(self.d)

    def __len__(self):
        return len(self.d)
