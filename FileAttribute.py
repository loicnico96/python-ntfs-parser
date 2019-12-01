
import Bytes
import Object
from NTFSReference import NTFSReference

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

class FileAttribute(object):
    type = 0x00
    length = 0x00
    resident = True
    name = ""

    def __init__(self, bytes):
        self.type = Bytes.toUnsigned32(bytes, 0x00)
        self.length = Bytes.toUnsigned32(bytes, 0x04)
        self.resident = not Bytes.toBoolean(bytes, 0x08)

        if self.resident:
            contentLength = Bytes.toUnsigned32(bytes, 0x10)
            contentOffset = Bytes.toUnsigned16(bytes, 0x14)
            self.content = bytes[contentOffset : contentOffset + contentLength]
            self.contentLength = contentLength
        else:
            dataRunOffset = Bytes.toUnsigned16(bytes, 0x20)
            contentLength = Bytes.toUnsigned64(bytes, 0x30)
            self.dataruns = parseDataRuns(bytes[dataRunOffset:])
            self.contentLength = contentLength

        if self.type == 0x10:
            self.name = "$Standard_Information"
        elif self.type == 0x30:
            self.name = "$File_Name"
            if self.content:
                filenameLength = Bytes.toUnsigned8(self.content, 0x40)
                self.filename = Bytes.toString16(self.content, 0x42, filenameLength)
                parentIndex = Bytes.toUnsigned64(self.content, 0x00) & 0x00FFFFFF
                parentSequence = Bytes.toUnsigned16(self.content, 0x06)
                self.parentRef = NTFSReference(parentIndex, parentSequence)
                self.size = Bytes.toUnsigned64(self.content, 0x30)
        elif self.type == 0x80:
            self.name = "$Data"
        elif self.type == 0x90:
            self.name = "$Index_Root"
        elif self.type == 0xA0:
            self.name = "$Index_Allocation"

    def __repr__(self):
        return Object.inspect("FileAttribute")

    def __str__(self):
        return Object.inspect("FileAttribute", self)
