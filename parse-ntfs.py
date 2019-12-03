
import sys
import NTFS.Bytes as Bytes
from NTFS.NTFSDrive import NTFSDrive
from NTFS.Win32FileReader import Win32FileReader

KILOBYTES = 2**10
MEGABYTES = 2**20
GIGABYTES = 2**30

if len(sys.argv) < 2:
    raise RuntimeError('Missing command line argument: py main.py "drivename"')
driveName = sys.argv[1]
driveReader = Win32FileReader(driveName)
drive = NTFSDrive(driveName, driveReader)

print('Opened NTFS drive "%s"' % driveName)

config = drive.config()
bytesPerSector = config.bytesPerSector
sectorsPerCluster = config.sectorsPerCluster
totalSize = config.totalSectors * config.bytesPerSector
print('Bytes per sector: %d' % bytesPerSector)
print('Sectors per cluster: %d' % sectorsPerCluster)
print('Total size: %.2fGb (%d)' % (float(totalSize) / GIGABYTES, totalSize))

cd = drive.root()

while True:
    print('')
    try:
        input = raw_input('%s>' % cd.fullname()).split()
        argv = input[1:]
        argc = len(argv)
        cmd = input[0]

        if cmd == 'exit':
            if argc != 0:
                raise IOError('This command excepted %d parameters, received %d.' % (0, argc))
            break
        elif cmd == 'dir':
            if argc != 0:
                raise IOError('This command excepted %d parameters, received %d.' % (0, argc))
            cd.children().dump()
        elif cmd == 'cd':
            if argc != 1:
                raise IOError('This command excepted %d parameters, received %d.' % (1, argc))
            pathElements = argv[0].replace('/', '\\').split('\\')
            cdNew = cd
            for pathElement in pathElements:
                if pathElement == '..':
                    cdNew = cdNew.parent()
                elif pathElement != '.':
                    cdNew = cdNew.child(pathElement)
                if not cdNew:
                    raise IOError('This path does not exist.')
                if not cdNew.isDir():
                    content = cdNew.content()
                    if content:
                        Bytes.dump(content, maxLines = 100)
                    else:
                        for attr in cdNew.attributes():
                            print(attr)
                    raise IOError('This path is not a directory.')
            cd = cdNew
        else:
            raise IOError('This command does not exist.')
    except IOError as io:
        print('Invalid input: %s' % io)
    #except Exception as exception:
    #    print(exception)
