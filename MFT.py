from Headers import mft_header
from attribute import Attribute
from fs_file_reader import FSFileReader


class MFT:

    MFT_ENTRY_SIZE = 1024

    def __init__(self, fs_file_path: str):
        """
        Parse the MFT file and save info about the MFT file

        :param fs_file_path: filesystem path
        """

        self.filesystem_reader = FSFileReader(fs_file_path)
        # CR: [implementation] This is awkward... If only FSFileReader could
        # read less than a cluster...
        # CR: [implementation] Break non-trivial logic to a function with a
        # meaningful name
        mft_entry_0 = self.filesystem_reader.get_clusters(
            self.filesystem_reader.mft_starting_cluster, 1)[:self.MFT_ENTRY_SIZE]
        self._mft_header = mft_header.MftHeader(mft_entry_0)
        mft_entry_0 = self._mft_header.get_origin_mft_entry_bytes(mft_entry_0)
        # CR: [design] Why is the mft aware of attributes?
        attributes_bytes = mft_entry_0[self._mft_header.attributes_offset:]
        self._mft_file_bytes = self._get_mft_bytes(attributes_bytes)
        self.mft_max_index = int(len(self._mft_file_bytes) / self.MFT_ENTRY_SIZE)

    # CR: [design] This function speaks in the language of atributes insted of
    # the language of entries.
    # CR: [design] Why not use the File class abstraction for this?
    def _get_mft_bytes(self, attributes_bytes: bytes) -> bytes:
        """
        Return the mft file bytes

        :param attributes_bytes: the attributes bytes to parse
        :return: mft file bytes
        """

        attribute = Attribute(attributes_bytes, self.filesystem_reader)
        # CR: [finish] Don't use magic numbers!
        while attribute.attribute_identifier != 128:
            attributes_bytes = attributes_bytes[attribute.attribute_length:]
            attribute = Attribute(attributes_bytes, self.filesystem_reader)
        return attribute.content

    # CR: [design] Why return bytes and not and entry object
    def get_mft_entry(self, index: int) -> bytes:
        """
        Return the bytes of the wanted mft entry

        :param index: entry index
        :return: mft_entry: mft entry bytes
        """

        mft_entry_offset = index * self.MFT_ENTRY_SIZE
        if mft_entry_offset > len(self._mft_file_bytes):
            return bytes()
        return self._mft_file_bytes[mft_entry_offset: mft_entry_offset + self.MFT_ENTRY_SIZE]
