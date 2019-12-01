
import sys
import Bytes
import win32file
from pywintypes import Unicode
from AbstractFileReader import AbstractFileReader

class Win32FileReader(AbstractFileReader):
    __filename = None
    __handle = None

    def __init__(self, filename):
        self.__filename = filename
        try:
            fullname = '\\\\.\\%s' % filename
            self.__handle = win32file.CreateFile(fullname,
                win32file.GENERIC_READ,
                win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE,
                None,
                win32file.OPEN_EXISTING,
                0, 0)
            self.setPointer(0)
        except Exception as err:
            raise RuntimeError('Could not open the specified file.')

    def setPointer(self, offset):
        win32file.SetFilePointer(self.__handle, offset, win32file.FILE_BEGIN)

    def readBytes(self, length):
        rc, bytes = win32file.ReadFile(self.__handle, length)
        return bytes

    def filename(self):
        return self.__filename

    def close(self):
        win32file.CloseHandle(self.__handle)
