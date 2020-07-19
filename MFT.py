from FSFileReader import FSFileReader
from AttributeHeaderParser import AttributeHeaderParser
from DataAttributeParser import runlists_parse
from DataAttributeParser import get_data_size
from File import File


def mft_data_locations(mft_file_entry: bytes):
    """
    Return the runlists of the mft file

    :param mft_file_entry: bytes
    :return: mft_data_runlits : tuple (length: int, cluster: int)
    """

    attribute_header_parser = AttributeHeaderParser(mft_file_entry)
    return runlists_parse(attribute_header_parser.get_attribute_by_id(128)), \
        get_data_size(attribute_header_parser.get_attribute_by_id(128))


def filename_parser(entry_bytes: bytes):
    """
    Parse the given mft entry and return the name of the file

    :param entry_bytes: bytes
    :return: filename : str
    """

    if entry_bytes is None:
        return None

    attr_parser = AttributeHeaderParser(entry_bytes)

    filename_attribute_bytes = attr_parser.get_attribute_by_id(48)
    if filename_attribute_bytes is None:
        return None
    content_offset = int.from_bytes(filename_attribute_bytes[20:21], byteorder='little')
    filename_attribute_bytes = filename_attribute_bytes[content_offset:]
    name_len = int(filename_attribute_bytes[64]) * 2
    filename = filename_attribute_bytes[66:66 + name_len].decode().replace('\x00', '')
    return filename


class MFT(object):
    def __init__(self, fs_file_path: str):
        """
        Create MFT data handler

        :param fs_file_path:
        """

        self.filesystem_reader = FSFileReader(fs_file_path)
        res = mft_data_locations(self.filesystem_reader.get_cluster(self.filesystem_reader.boot_data.mft_start)
                                 [:self.filesystem_reader.get_record_size()])
        self.mft_sectors = res[0]
        self.mft_entries = int(res[1] / self.filesystem_reader.get_record_size())

    def get_mft_entry(self, index: int):
        """
        Return the mft entry bytes for the given index

        :param index: int
        :return: mft_entry: bytes
        """

        records_in_cluster = int(self.filesystem_reader.get_cluster_size() / self.filesystem_reader.get_record_size())
        cluster_num = int(index / records_in_cluster)
        current_cluster = 0
        for (length, cluster) in self.mft_sectors:
            current_cluster += cluster
            if length > cluster_num:
                current_cluster += cluster_num
                entry_offset = index % records_in_cluster * self.filesystem_reader.get_record_size()
                return current_cluster, entry_offset, \
                    self.filesystem_reader.get_cluster(current_cluster)[entry_offset:
                                                                        entry_offset + self.filesystem_reader.get_record_size()]
            else:
                cluster_num -= length
        return None

    def get_files_dict(self):
        """
        Create a file dictionary where the key is the file name and the value is the File object

        :return: files_dictionary : dict (key : filename, value : File object)
        """

        files = dict()
        for index in range(self.mft_entries):
            cluster, entry_offset, data = self.get_mft_entry(index)
            filename = filename_parser(data)
            if filename is not None:
                files[filename] = File(filename, entry_offset, cluster, self.filesystem_reader)
        return files
