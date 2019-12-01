
import Bytes
import Object

class NTFSDriveConfig(object):
    __bytesPerSec = 512
    __secPerClust = 8
    __mftOffset = 0
    __totalSec = 0

    def __init__(self, bytes):
        if bytes[0x03:0x07] != b'NTFS':
            raise ValueError("This is not a valid NTFS boot sector.")
        self.__bytesPerSec = Bytes.toUnsigned16(bytes, 0x0B)
        self.__secPerClust = Bytes.toUnsigned8(bytes, 0x0D)
        self.__mftOffset = Bytes.toUnsigned64(bytes, 0x30)
        self.__totalSec = Bytes.toUnsigned64(bytes, 0x28)

    def __repr__(self):
        return Object.inspect("NTFSDriveConfig")

    def __str__(self):
        return Object.inspect("NTFSDriveConfig", self)

    @property
    def totalSectors(self):
        return self.__totalSec

    @property
    def bytesPerSector(self):
        return self.__bytesPerSec

    @property
    def sectorsPerCluster(self):
        return self.__secPerClust

    @property
    def mftOffset(self):
        return self.__mftOffset

# Virtual Boot Sector:
# Size  Offset  Content
# 3     0x0000  chJumpInstruction
# 4     0x0003  chOemID
# 4     0x0007  chDummy
# 2     0x000B  wBytesPerSec
# 1     0x000D  uchSecPerClust
# 2     0x000E  wReservedSec
# 3     0x0010  uchReserved
# 2     0x0013  dwUnused1
# 1     0x0015  uchMediaDescriptor
# 2     0x0016  dwUnused2
# 2     0x0018  wSecPerTrack
# 2     0x001A  wNumberOfHeads
# 4     0x001C  dwHiddenSec
# 4     0x0020  dwUnused3
# 4     0x0024  dwUnused4
# 8     0x0028  n64TotalSec
# 8     0x0030  n64MFTLoficalClustNum
# 8     0x0038  n64MFTMirrLogicalClustNum
# 4     0x0040  nClustPerMFTRecord
# 4     0x0044  nClustPerIndexRecord
# 8     0x0048  n64VolumeSerialNum
# 4     0x0050  dwChecksum
# 426   0x0054  chBootstrapCode
# 2     0x01FE  wSecMark
