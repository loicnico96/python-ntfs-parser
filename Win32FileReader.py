
import win32file
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
        except Exception as err:
            raise RuntimeError('Could not open the specified file.')

    def isValid(self):
        return self.__handle != None

    def readBytes(self, offset, length):
        if self.__handle == None:
            raise RuntimeError('Could not read from an invalid file handle.')
        win32file.SetFilePointer(self.__handle, offset, win32file.FILE_BEGIN)
        rc, bytes = win32file.ReadFile(self.__handle, length)
        return bytes

    def filename(self):
        return self.__filename

    def close(self):
        if self.__handle == None:
            raise RuntimeError('Could not close an invalid file handle.')
        win32file.CloseHandle(self.__handle)
        self.__handle = None
