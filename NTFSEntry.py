
import Bytes
import Object
from FileAttribute import FileAttribute
from NTFSReference import NTFSReference
from NTFSFileIndex import NTFSFileIndex

MFT_ENTRY_SECTORS = 2
FILE_SEPARATOR = "\\"

class NTFSEntry(object):
    __attributes = []
    __children = None
    __content = None
    __contentSize = 0
    __drive = None
    __filename = None
    __index = 0L
    __isDir = False
    __parent = None
    __parentRef = None
    __sequence = 0

    def __init__(self, drive, index):
        self.__drive = drive
        self.__index = index

        # Retrieve the MFT entry from the drive
        drive.reader().setPointer(drive.entryOffset(index))
        entryLength = MFT_ENTRY_SECTORS * drive.config().bytesPerSector
        entryBytes = drive.reader().readBytes(entryLength)

        # Check if the header is correct
        if entryBytes[0x00:0x04] != b'FILE':
            raise ValueError("This is not a valid FILE entry.")

        # Parse the MFT header information
        attrOffset = Bytes.toUnsigned16(entryBytes, 0x14)
        fileFlags = Bytes.toUnsigned16(entryBytes, 0x16)
        self.__sequence = Bytes.toUnsigned16(entryBytes, 0x10)
        self.__isDir = bool(fileFlags & 0x02)
        self.__attributes = []

        # Parse the FILE attributes
        while Bytes.toUnsigned32(entryBytes, attrOffset) != 0xFFFFFFFF:
            attrLength = Bytes.toUnsigned16(entryBytes, attrOffset+0x04)
            attrObject = FileAttribute(entryBytes[attrOffset:attrOffset+attrLength])
            self.__attributes.append(attrObject)
            attrOffset += attrLength

        # Cache important attributes such as filename
        attrFileName = self.attribute(0x30)
        self.__filename = attrFileName.filename
        self.__parentRef = attrFileName.parentRef
        self.__contentSize = attrFileName.size

    def __repr__(self):
        return Object.inspect("NTFSEntry")

    def __str__(self):
        return Object.inspect("NTFSEntry", self)

    @property
    def drive(self):
        return self.__drive

    @property
    def index(self):
        return self.__index

    @property
    def sequence(self):
        return self.__sequence

    @property
    def parentRef(self):
        return self.__parentRef

    def parent(self, count = 1):
        if self.__parentRef == None:
            return None
        if self.__parentRef.index == self.__index:
            return None
        if self.__parent == None:
            self.__parent = self.__drive.entry(self.__parentRef)
        if self.__parent != None and count > 1:
            return self.__parent.parent(count - 1)
        return self.__parent

    def isDir(self):
        return self.__isDir

    def filename(self):
        return self.__filename

    def path(self):
        if self.parent() != None:
            return self.parent().fullname()
        return self.__drive.driveName()

    def fullname(self):
        if self.filename() == ".":
            return self.path()
        return FILE_SEPARATOR.join([self.path(), self.filename()])

    def attributes(self):
        return self.__attributes

    def attribute(self, type):
        return Object.find(self.attributes(), lambda attr: attr.type == type)

    def contentSize(self):
        return self.__contentSize

    def children(self):
        if self.__children != None:
            return self.__children
        if self.__isDir:
            indexRoot = self.attribute(0x90)
            indexAlloc = self.attribute(0xA0)
            if indexAlloc != None:
                records = []
                recordIndex = 0
                clusterSize = self.__drive.config().sectorsPerCluster * self.__drive.config().bytesPerSector
                dataruns = indexAlloc.dataruns
                for datarun in dataruns:
                    recordSize = datarun[1] * clusterSize
                    recordIndex = recordIndex + datarun[0]
                    self.__drive.reader().setPointer(self.__drive.clusterOffset(recordIndex))
                    record = self.__drive.reader().readBytes(recordSize)
                    records.append(record)
                self.__children = NTFSFileIndex(self.__drive, indexRoot, records)
            else:
                self.__children = NTFSFileIndex(self.__drive, indexRoot)
            return self.__children
        return None

    def childRef(self, filename):
        return self.children().ref(filename)

    def child(self, filename):
        return self.children().entry(filename)
