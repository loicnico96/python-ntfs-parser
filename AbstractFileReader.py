
from abc import ABCMeta, abstractmethod

class AbstractFileReader(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def readBytes(self, offset, length):
        raise NotImplementedError('Not implemented.')

    @abstractmethod
    def close(self):
        raise NotImplementedError('Not implemented.')
