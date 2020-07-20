from FSFileReader import FSFileReader
from AttributeHeaderParser import AttributeHeaderParser
from DataAttributeParser import runlists_parse
from DataAttributeParser import get_data_size
from File import File


def mft_data_locations(mft_file_entry: bytes, filesystem_reader: FSFileReader):
    """
    Return the data runlists of the mft file

    :param filesystem_reader: FSFileReader
    :param mft_file_entry: bytes
    :return: mft_data_runlits : tuple (length: int, cluster: int)
    """

    attribute_header_parser = AttributeHeaderParser(mft_file_entry)
    data_attributes = attribute_header_parser.get_attribute_by_id(128)
    runlists = []
    data_size = 0
    for data_attribute in data_attributes:
        res = runlists_parse(data_attribute)
        for runlist in res:
            runlists.append(runlist)
        data_size += get_data_size(data_attribute)
    return runlists, data_size


class MFT(object):
    def __init__(self, fs_file_path: str):
        """
        Create MFT data handler

        :param fs_file_path:
        """

        self.filesystem_reader = FSFileReader(fs_file_path)
        res = mft_data_locations(self.filesystem_reader.get_cluster(self.filesystem_reader.boot_data.mft_start)
                                 [:self.filesystem_reader.get_record_size()], self.filesystem_reader)
        self.mft_sectors = res[0]
        self.mft_entries = int(res[1] / self.filesystem_reader.get_record_size())

    def get_mft_entry(self, index: int):
        """
        Return the string cluster, entry offeset and the mft entry bytes for the given index

        :param index: int
        :return: tuple(string cluster for the entry: int, offset in the cluster: int, the mft entry bytes: bytes)
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

    def search_attribute_list(self, attribute_bytes: bytes, needed_id: int, entry_index: int):
        """
        Search the attribute list for the needed attribute and return the bytes of the attributes found

        :param attribute_bytes:
        :param needed_id:
        :param entry_index:
        :return:
        """
        
        attributes = []
        attribute_length = len(attribute_bytes)

        current_pos = 0
        while current_pos < attribute_length:
            attribute_id = int.from_bytes(attribute_bytes[current_pos: current_pos + 3], byteorder='little')
            attribute_size = int.from_bytes(attribute_bytes[current_pos + 4: current_pos + 5], byteorder='little')
            if attribute_id == needed_id:
                attribute_location = int.from_bytes(attribute_bytes[current_pos + 16: current_pos + 21],
                                                    byteorder='little')
                if attribute_location != entry_index:
                    _, _, data = self.get_mft_entry(attribute_location)
                    attr_parser = AttributeHeaderParser(data)
                    res = attr_parser.get_attribute_by_id(needed_id)
                    if res is not None:
                        for attribute in res:
                            if attribute is not None:
                                attributes.append(attribute)

            current_pos += attribute_size
        return attributes

    def attribute_search(self, entry_bytes: bytes, needed_id: int, entry_index: int):
        """
        Search for the wanted attribute in the mft entry, include the attributes_list attribute and return the bytes of the attributes

        :param entry_bytes: bytes
        :param entry_index: int
        :param needed_id: int
        :return: list(bytes)
        """

        attributes = []

        attr_parser = AttributeHeaderParser(entry_bytes)
        attr_list = attr_parser.get_attribute_by_id(32)
        if len(attr_list) != 0:
            attr_list_attributes = self.search_attribute_list(attr_list, needed_id, entry_index)
            if attr_list_attributes is not None:
                for attribute in attr_list_attributes:
                    attributes.append(attribute)

        res = attr_parser.get_attribute_by_id(needed_id)
        if len(res) != 0:
            for attribute in res:
                if attribute is not None:
                    attributes.append(attribute)

        return attributes

    def filename_parser(self, entry_bytes: bytes, entry_index: int):
        """
        Parse the given mft entry and return the all the names of the file

        :param entry_index: int
        :param entry_bytes: bytes
        :return: filename : list(filenames: str)
        """

        filename_attributes_bytes = self.attribute_search(entry_bytes, 48, entry_index)
        if len(filename_attributes_bytes) == 0:
            return None

        filenames = []

        for filename_attribute_bytes in filename_attributes_bytes:
            if filename_attribute_bytes is None:
                return None
            content_offset = int.from_bytes(filename_attribute_bytes[20:21], byteorder='little')
            filename_attribute_bytes = filename_attribute_bytes[content_offset:]
            name_len = int(filename_attribute_bytes[64]) * 2
            filename = filename_attribute_bytes[66:66 + name_len].decode().replace('\x00', '')
            filenames.append(filename)

        return filenames

    def get_files_dict(self):
        """
        Create a file dictionary where the key is the file name and the value is the File object

        :return: files_dictionary : dict (key : filename, value : File object)
        """

        files = dict()
        for index in range(self.mft_entries):
            cluster, entry_offset, data = self.get_mft_entry(index)
            filenames = self.filename_parser(data, index)
            if filenames is None:
                continue
            for filename in filenames:
                if filename is not None:
                    files[filename] = File(filename, entry_offset, cluster, self.filesystem_reader, index)
        return files
