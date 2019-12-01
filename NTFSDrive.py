
import Object
from NTFSEntry import NTFSEntry
from NTFSDriveConfig import NTFSDriveConfig
from NTFSReference import NTFSReference

BOOT_SECTOR_OFFSET = 0
BOOT_SECTOR_LENGTH = 512
MFT_ROOT_INDEX = 5

class NTFSDrive(object):
    __driveName = None
    __fileReader = None
    __config = None
    __root = None

    def __init__(self, driveName, fileReader):
        self.__driveName = driveName
        self.__fileReader = fileReader
        # Fetch the configuration from the Virtual Boot Sector
        vbsBytes = self.__fileReader.readBytes(BOOT_SECTOR_OFFSET, BOOT_SECTOR_LENGTH)
        self.__config = NTFSDriveConfig(vbsBytes)
        # Fetch the root entry in the Master File Table
        self.__root = NTFSEntry(self, MFT_ROOT_INDEX)

    def __repr__(self):
        return Object.inspect("NTFSDrive")

    def __str__(self):
        return Object.inspect("NTFSDrive", self)

    def driveName(self):
        return self.__driveName

    def reader(self):
        return self.__fileReader

    def config(self):
        return self.__config

    def root(self):
        return self.__root

    def entry(self, reference):
        if isinstance(reference, NTFSReference):
            entry = NTFSEntry(self, reference.index)
            if entry.sequence != 0 and reference.sequence != 0 and entry.sequence != reference.sequence:
                print("Incoherent sequence.")
        else:
            entry = NTFSEntry(self, reference)
        return entry

    def file(self, fullname):
        entry = self.root()
        pathElements = fullname.replace("/", "\\").split("\\")
        if pathElements[0] == self.__driveName:
            pathElements = pathElements[1:]
        for element in pathElements:
            entry = entry.child(element)
            if entry == None:
                return None
        return entry

    def sectorOffset(self, sectorIndex):
        return sectorIndex * self.config().bytesPerSector

    def clusterOffset(self, clusterIndex):
        return self.sectorOffset(clusterIndex * self.config().sectorsPerCluster)

    def entryOffset(self, entryIndex):
        return self.sectorOffset(self.config().mftOffset * self.config().sectorsPerCluster + entryIndex * 2)
