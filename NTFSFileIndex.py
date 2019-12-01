
import Bytes
import Object
from datetime import datetime
from FileAttribute import FileAttribute
from NTFSReference import NTFSReference

MAGIC_WORD_INDX = b'INDX'

TAG_ALIAS = '<ALIAS>'
TAG_DIRECTORY = '<DIR>'

def toUNIX(timestamp):
    return max(0, timestamp / 1e7 - 11644473600)

class NTFSFileIndex(object):
    __drive = None
    __entries = []

    def addRecord(self, bytes, offset = 0):
        while True:
            length = Bytes.toUnsigned16(bytes, offset+0x08)
            attrLength = Bytes.toUnsigned16(bytes, offset+0x0A)
            fileIndex = Bytes.toUnsigned64(bytes, offset+0x00) & 0x00FFFFFF
            fileSeq = Bytes.toUnsigned16(bytes, offset+0x06)
            flags = Bytes.toUnsigned8(bytes, offset+0x0C)

            if flags & 0x01:
                indexAllocation = Bytes.toUnsigned64(bytes, offset+length-8)
            if flags & 0x02:
                break

            attrBytes = bytes[offset+0x10:offset+0x10+attrLength]
            filenameLength = Bytes.toUnsigned8(attrBytes, 0x40)
            filename = Bytes.toString16(attrBytes, 0x42, filenameLength)
            isDir = bool(Bytes.toUnsigned32(attrBytes, 0x38) & 0x10000000)
            contentSize = Bytes.toUnsigned64(attrBytes, 0x30)
            tsCreated = toUNIX(Bytes.toUnsigned64(attrBytes, 0x08))
            tsModified = toUNIX(Bytes.toUnsigned64(attrBytes, 0x10))
            self.__entries.append((fileIndex, fileSeq, filename, isDir, contentSize, tsCreated, tsModified))
            offset += length

    def __init__(self, drive, indexRoot, indexRecords = []):
        bytes = indexRoot.content
        self.__drive = drive
        self.__entries = []
        self.attributeType = Bytes.toUnsigned32(bytes, 0x00)
        self.collationRule = Bytes.toUnsigned32(bytes, 0x04)
        self.bytesPerIndexRecord = Bytes.toUnsigned32(bytes, 0x08)
        self.clustersPerIndexRecord = Bytes.toUnsigned8(bytes, 0x0C)
        startingOffset = Bytes.toUnsigned32(bytes, 0x10) + 0x10
        self.addRecord(bytes, startingOffset)

        for bytes in indexRecords:
            if bytes[0x00:0x04] != MAGIC_WORD_INDX:
                raise ValueError('This is not a valid INDX record.')
            startingOffset = Bytes.toUnsigned32(bytes, 0x18) + 0x18
            self.addRecord(bytes, startingOffset)

    def __repr__(self):
        return Object.inspect('NTFSFileIndex')

    def __str__(self):
        return Object.inspect('NTFSFileIndex', self)

    def ref(self, filename):
        ent = Object.find(self.__entries, lambda ent: ent[2] == filename)
        return NTFSReference(ent[0], ent[1]) if ent else None

    def entry(self, filename):
        ref = self.ref(filename)
        return self.__drive.entry(ref) if ref else None

    def filenames(self):
        return [ent[2] for ent in self.__entries]

    def list(self):
        res = []
        totalDirs = 0
        totalSize = 0
        totalFiles = 0
        indexes = set()
        for ent in self.__entries:
            index, sequence, filename, isDir, contentSize, tsCreated, tsModified = ent
            if index in indexes:
                sz = format(TAG_ALIAS, '<14')
            elif isDir:
                totalDirs += 1
                sz = format(TAG_DIRECTORY, '<14')
            else:
                totalFiles += 1
                totalSize += contentSize
                sz = format(contentSize, '>14,').replace(',', ' ')
            dt = datetime.fromtimestamp(tsModified).strftime('%d/%m/%Y  %H:%M')
            des = '{0:<20}{1:<15}{2}'.format(dt, sz, filename)
            indexes.add(index)
            res.append(des)
        ttf = '{0:,} files'.format(totalFiles)
        ttd = '{0:,} directories'.format(totalDirs)
        tts = '{0:,} bytes'.format(totalSize).replace(',', ' ')
        res.append('{0:<15}{1:<15}{2}'.format('', ttf, tts))
        res.append('{0:<15}{1}'.format('', ttd))
        return res

    def refs(self):
        return [NTFSReference(ent[0], ent[1]) for ent in self.__entries]

    def entries(self):
        refs = self.refs()
        return [self.__drive.entry(ref) for ref in refs]
