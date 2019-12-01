
import math
from struct import unpack, calcsize

def fromFile(filename):
    with open(filename, "rb") as file:
        content = file.read()
        file.close()
    return content

def toString(charSize, encoding, bytes, offset = 0, length = None):
    endOffset = offset+length*charSize if length else None
    return bytes[offset:endOffset].decode(encoding)

def toString8(bytes, offset = 0, length = None):
    return toString(1, "utf-8", bytes, offset, length)

def toString16(bytes, offset = 0, length = None):
    return toString(2, "utf-16", bytes, offset, length)

def toFormat(format, bytes, offset = 0):
    endOffset = offset+calcsize(format)
    return unpack(format, bytes[offset:endOffset])[0]

def toBoolean(bytes, offset = 0):
    return toFormat("<?", bytes, offset)

def toSigned8(bytes, offset = 0):
    return toFormat("<b", bytes, offset)

def toUnsigned8(bytes, offset = 0):
    return toFormat("<B", bytes, offset)

def toSigned16(bytes, offset = 0):
    return toFormat("<h", bytes, offset)

def toUnsigned16(bytes, offset = 0):
    return toFormat("<H", bytes, offset)

def toSigned32(bytes, offset = 0):
    return toFormat("<i", bytes, offset)

def toUnsigned32(bytes, offset = 0):
    return toFormat("<I", bytes, offset)

def toSigned64(bytes, offset = 0):
    return toFormat("<q", bytes, offset)

def toUnsigned64(bytes, offset = 0):
    return toFormat("<Q", bytes, offset)

def toUnsigned(bytes, offset = 0, words = 4):
    uint = 0
    for i in range(0, words):
        uint += toUnsigned8(bytes, offset + i) << (8 * i)
    return uint

def dump(bytes, offset = 0, length = None, lineLength = 16, maxLines = 32):
    byteLength = len(bytes) - offset if length == None else length
    lineCount = (byteLength + lineLength - 1) / lineLength
    if length == None and maxLines != None:
        lineCount = min(maxLines, lineCount)
    for lineIndex in range(0, lineCount):
        lineOffset = offset + lineIndex * lineLength
        lineBytes = bytes[lineOffset:lineOffset+lineLength]
        lineHex = [byte.encode("hex") for byte in lineBytes]
        lineChr = [byte.encode("ascii") if (byte>=b'\x20' and byte<=b'\x7E') else "." for byte in lineBytes]
        for fillRemaining in range(len(lineBytes), lineLength):
            lineHex.append("  ")
            lineChr.append(" ")

        print("%08x  %s  %s" % (lineOffset, " ".join(lineHex), "".join(lineChr)))
