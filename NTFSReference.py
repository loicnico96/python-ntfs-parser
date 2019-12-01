
import Object

class NTFSReference(object):
    __index = 0L
    __sequence = 0

    def __init__(self, index, sequence):
        self.__index = index
        self.__sequence = sequence

    def __repr__(self):
        return Object.inspect("NTFSReference")

    def __str__(self):
        return Object.inspect("NTFSReference", self)

    @property
    def index(self):
        return self.__index

    @property
    def sequence(self):
        return self.__sequence
