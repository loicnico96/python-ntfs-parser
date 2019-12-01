
import Bytes
import Object
from NTFSReference import NTFSReference

ATTR_TYPE_STANDARD_INFO = 0x10
ATTR_NAME_STANDARD_INFO = '$Standard_Information'
ATTR_TYPE_FILENAME = 0x30
ATTR_NAME_FILENAME = '$File_Name'
ATTR_TYPE_DATA = 0x80
ATTR_NAME_DATA = '$Data'
ATTR_TYPE_INDEX_ROOT = 0x90
ATTR_NAME_INDEX_ROOT = '$Index_Root'
ATTR_TYPE_INDEX_ALLOC = 0xA0
ATTR_NAME_INDEX_ALLOC = '$Index_Allocation'

def parseDataRuns(bytes, offset = 0x00):
    index = offset
    dataruns = []
    while True:
        sizeInfo = Bytes.toUnsigned8(bytes, index)
        if sizeInfo == 0x00:
            break

        clusterCountSize = int(sizeInfo % 0x10)
        clusterIndexSize = int(sizeInfo / 0x10)
        index += 0x01

        clusterCount = Bytes.toUnsigned(bytes, index, clusterCountSize)
        index += clusterCountSize

        clusterIndex = Bytes.toUnsigned(bytes, index, clusterIndexSize)
        index += clusterIndexSize

        dataruns.append((clusterIndex, clusterCount))
    return dataruns

class NTFSAttribute(object):
    __content = None
    __contentLength = 0
    __dataruns = None
    __name = ''
    __resident = True
    __type = 0x00

    def __init__(self, bytes):
        self.__type = Bytes.toUnsigned32(bytes, 0x00)
        self.__resident = not Bytes.toBoolean(bytes, 0x08)

        if self.__resident:
            contentLength = Bytes.toUnsigned32(bytes, 0x10)
            contentOffset = Bytes.toUnsigned16(bytes, 0x14)
            self.__content = bytes[contentOffset : contentOffset + contentLength]
            self.__contentLength = contentLength
        else:
            dataRunOffset = Bytes.toUnsigned16(bytes, 0x20)
            contentLength = Bytes.toUnsigned64(bytes, 0x30)
            self.__dataruns = parseDataRuns(bytes[dataRunOffset:])
            self.__contentLength = contentLength

        if self.__type == ATTR_TYPE_STANDARD_INFO:
            self.__name = ATTR_NAME_STANDARD_INFO
        elif self.__type == ATTR_TYPE_FILENAME:
            self.__name = ATTR_NAME_FILENAME
            if self.__content:
                filenameLength = Bytes.toUnsigned8(self.__content, 0x40)
                self.filename = Bytes.toString16(self.__content, 0x42, filenameLength)
                parentIndex = Bytes.toUnsigned64(self.__content, 0x00) & 0x00FFFFFF
                parentSequence = Bytes.toUnsigned16(self.__content, 0x06)
                self.parentRef = NTFSReference(parentIndex, parentSequence)
                self.size = Bytes.toUnsigned64(self.__content, 0x30)
        elif self.__type == ATTR_TYPE_DATA:
            self.__name = ATTR_NAME_DATA
        elif self.__type == ATTR_TYPE_INDEX_ROOT:
            self.__name = ATTR_NAME_INDEX_ROOT
        elif self.__type == ATTR_TYPE_INDEX_ALLOC:
            self.__name = ATTR_NAME_INDEX_ALLOC

    def __repr__(self):
        return Object.inspect('NTFSAttribute')

    def __str__(self):
        return Object.inspect('NTFSAttribute', self)

    def type(self):
        return self.__type

    def name(self):
        return self.__name

    def dataruns(self):
        return self.__dataruns

    def content(self):
        return self.__content

    def contentLength(self):
        return self.__contentLength

    def isResident(self):
        return self.__resident
