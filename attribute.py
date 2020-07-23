# CR: [finish] Import only what you need (from Headers.data_headers import ...)
from Headers import data_headers
from Headers import attriubte_header
from fs_file_reader import FSFileReader


class Attribute:

    def __init__(self, attribute_bytes: bytes, filesystem_reader: FSFileReader):

        self._attribute_header = attriubte_header.AttributeHeader(attribute_bytes)
        # CR: [design] Should have something like "if self.is_valid"
        if self._attribute_header.attribute_identifier > 0:
            # CR: [finish] Constants can be accessed as Class.Constant
            # (e.g. AttributeHeader.SIZE)
            attribute_data_end = self._attribute_header.ATTRIBUTE_HEADER_SIZE + self._attribute_header.attribute_length
            attribute_data_bytes = attribute_bytes[self._attribute_header.ATTRIBUTE_HEADER_SIZE: attribute_data_end]
            self._attribute_data = data_headers.AttributeData(attribute_data_bytes, self._attribute_header.is_resident,
                                                              filesystem_reader)

    @property
    def attribute_data_bytes(self):
        return self._attribute_data.get_attribute_data()

    @property
    def attribute_identifier(self):
        return self._attribute_header.attribute_identifier

    @property
    def attribute_length(self):
        return self._attribute_header.attribute_length

    @property
    def content(self):
        return self._attribute_data.get_attribute_data()
