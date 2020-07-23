import struct


class AttributeHeader:

    ATTRIBUTE_HEADER_SIZE = 16

    IDENTIFIER_PARSE = r'i'
    FORMAT = r'=4xIB'

    def __init__(self, attribute_bytes: bytes):
        """
        Parse the attribute header and save the parsed data

        :param attribute_bytes: the attribute bytes to parse
        """

        self.attribute_identifier = struct.unpack(self.IDENTIFIER_PARSE,
                                                  attribute_bytes[:struct.calcsize(self.IDENTIFIER_PARSE)])[0]
        if self.attribute_identifier != -1:
            self.attribute_length, \
                self.resident_flag = struct.unpack(self.FORMAT, attribute_bytes[:struct.calcsize(self.FORMAT)])

    @property
    def is_resident(self) -> bool:
        return self.resident_flag == 0
