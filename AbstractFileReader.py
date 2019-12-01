
from abc import ABCMeta, abstractmethod

class AbstractFileReader(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def setPointer(self, offset):
        raise NotImplementedError("setPointer(offset) was not implemented.")

    @abstractmethod
    def readBytes(self, length):
        raise NotImplementedError("readBytes(length) was not implemented.")

    @abstractmethod
    def close(self):
        raise NotImplementedError("close() was not implemented.")
