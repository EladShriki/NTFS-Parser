import typing
from Headers import mft_header
from attribute import Attribute
from fs_file_reader import FSFileReader
from filename_parser import FilenameParser


# CR: [finish] FileEntry might be a better name
class File(object):

    FILE_NAME_IDENTIFIER = 48
    DATA_IDENTIFIER = 128

    def __init__(self, mft_entry_bytes: bytes, mft_index: int, filesystem_reader: FSFileReader):
        """
        File handler, parse the file_entry and save info about the file

        :param mft_entry_bytes: mft entry bytes to parse
        :param mft_index: the mft entry index
        :param filesystem_reader: FSFileReader
        """

        # CR: [finish] This is unused, remove
        self._mft_index = mft_index
        self._filesystem_reader = filesystem_reader
        self._mft_header = mft_header.MftHeader(mft_entry_bytes)
        mft_entry_bytes = self._mft_header.get_origin_mft_entry_bytes(mft_entry_bytes)
        attributes_bytes = mft_entry_bytes[self._mft_header.attributes_offset:]
        self.file_names, self._data_attributes = self._attributes(attributes_bytes)

    # CR: [conventions] Write functions top down
    def _attributes(self, attributes_bytes: bytes) -> typing.Tuple[typing.List[str], typing.List[Attribute]]:
        """
        Parse the attributes in the mft entry

        :param attributes_bytes: the attributes bytes to parse
        :return: the file names found and the data attributes
        """

        if not self._mft_header.is_allocated:
            return [], []

        file_names = []
        data_attributes = []

        attribute = Attribute(attributes_bytes, self._filesystem_reader)
        while attribute.attribute_identifier != -1:
            if attribute.attribute_identifier == self.FILE_NAME_IDENTIFIER:
                file_names.append(FilenameParser(attribute).filename)
            if attribute.attribute_identifier == self.DATA_IDENTIFIER:
                data_attributes.append(attribute)
            attributes_bytes = attributes_bytes[attribute.attribute_length:]
            attribute = Attribute(attributes_bytes, self._filesystem_reader)
        return file_names, data_attributes

    # CR: [design] +1 for the simplicity of this function
    def get_content(self) -> bytes:
        """
        Read the current file data with the data parser and return the file data

        :return: file_data : the file content
        """

        data = bytes()

        for data_attribute in self._data_attributes:
            data += data_attribute.content

        return data

