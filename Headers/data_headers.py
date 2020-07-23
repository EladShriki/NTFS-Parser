import struct
from runlist import Runlists
from Headers import attriubte_header
from fs_file_reader import FSFileReader


class AttributeData:
    def __init__(self, attribute_bytes: bytes, resident: bool, filesystem_reader: FSFileReader):
        """
        Parse the attribute data and save the attribute data

        :param attribute_bytes: the attribute bytes to parse
        :param resident: is the attribute is resident
        :param filesystem_reader: FSFileReader
        """

        if resident:
            self._data_header = ResidentHeader(attribute_bytes)
        else:
            self._data_header = NonResidentHeader(attribute_bytes, filesystem_reader)

    def get_attribute_data(self) -> bytes:
        return self._data_header.content


class ResidentHeader:

    RESIDENT_HEADER_SIZE = 6
    FORMAT = r'=IH'

    def __init__(self, header_bytes: bytes):
        """
        Parse the Resident header and save the attribute data

        :param header_bytes: bytes
        """

        self._content_size,\
            self._content_offset = struct.unpack(self.FORMAT, header_bytes[:struct.calcsize(self.FORMAT)])
        fixed_offset = self._content_offset - attriubte_header.AttributeHeader.ATTRIBUTE_HEADER_SIZE
        self.content = header_bytes[fixed_offset: fixed_offset + self._content_size]


class NonResidentHeader:

    NON_RESIDENT_HEADER_SIZE = 48
    FORMAT = r'=QQH14xQ'

    def __init__(self, header_bytes: bytes, filesystem_reader: FSFileReader):
        """
        Parse the non resident header and the runlists

        :param header_bytes: bytes
        :param filesystem_reader: FSFileReader
        """

        self._start_VCN, \
            self._end_VCN, \
            self._runlist_offset, \
            self._content_size = struct.unpack(self.FORMAT, header_bytes[:struct.calcsize(self.FORMAT)])

        self._runlist_offset = self._runlist_offset - 16
        self._runlists = Runlists(header_bytes[self._runlist_offset:], filesystem_reader)

    @property
    def content(self) -> bytes:
        return self._runlists.get_data()[:self._content_size]
