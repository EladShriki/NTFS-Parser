import struct
from attribute import Attribute


class FilenameParser:

    FORMAT = r'=64xB'
    FILE_NAME_OFFSET = 66

    def __init__(self, attribute: Attribute):
        """
        Parse the filename attribute and save the file name

        :param attribute: filename attribute to parse
        """

        filename_bytes = attribute.attribute_data_bytes
        self.filename_size = struct.unpack(self.FORMAT, filename_bytes[:struct.calcsize(self.FORMAT)])[0] * 2
        self.filename = filename_bytes[self.FILE_NAME_OFFSET:
                                       self.FILE_NAME_OFFSET + self.filename_size].decode('utf16')
