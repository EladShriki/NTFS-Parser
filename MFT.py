from FSFileReader import FSFileReader
from AttributeHeaderParser import AttributeHeaderParser
from DataAttributeParser import runlists_parse
from DataAttributeParser import get_data_size
from File import File


# CR: [design] You seem to implement here the same logic that is implemented by
# the File class to retrieve data. Why?

# CR: [design] Why is this detached from a class?
# CR: [finish] Why is it named mft_data_locations if it doesn't operate on the
# MFT? Does this work only for the MFT entry?
def mft_data_locations(mft_file_entry: bytes, filesystem_reader: FSFileReader):
    """
    Return the data runlists of the mft file

    :param filesystem_reader: FSFileReader
    :param mft_file_entry: bytes
    :return: mft_data_runlits : tuple (length: int, cluster: int)
    """

    attribute_header_parser = AttributeHeaderParser(mft_file_entry)
    # CR: [finish] Don't use magic numbers
    data_attributes = attribute_header_parser.get_attribute_by_id(128)
    runlists = []
    data_size = 0
    for data_attribute in data_attributes:
        # CR: [finish] res is a bad name
        # CR: [implementation] Assuming res is a list you could just use
        # runlists += runlists_parse(data_attribute)
        res = runlists_parse(data_attribute)
        for runlist in res:
            runlists.append(runlist)
        data_size += get_data_size(data_attribute)
    return runlists, data_size


# CR: [finish] In python3 there's no need to explicitly inherit from object
class MFT(object):
    def __init__(self, fs_file_path: str):
        """
        Create MFT data handler

        :param fs_file_path:
        """

        self.filesystem_reader = FSFileReader(fs_file_path)
        # CR: [finish] res is a bad name
        # CR: [finish] Break this line to multiple statements to make it
        # clearer.
        # CR: [design] You break encapsulation here!
        res = mft_data_locations(self.filesystem_reader.get_cluster(self.filesystem_reader.boot_data.mft_start)
                                 [:self.filesystem_reader.get_record_size()], self.filesystem_reader)
        # CR: [finish] Your names are very non-intuitive! mft_sectors doesn't
        # hold sectors and mft_entries doesn't hold entries. Try something like
        # mft_runlists and mft_entry_num
        # CR: [design] Should an MFT be aware of low level details such as run
        # lists?
        self.mft_sectors = res[0]
        # CR: [robustness] What does it mean if res[1] is not a multiple of the
        # record size? Is that a legitimate situation?
        self.mft_entries = int(res[1] / self.filesystem_reader.get_record_size())

    def get_mft_entry(self, index: int):
        # CR: [finish] What does string cluster (which is an int) mean?
        # CR: [requirements] Are you allowed to assume that a file entry is a
        # multiple of sector size?
        # CR: [design/performance] Let's talk about the option of reading the
        # entire MFT once and then parsing it in memory.
        """
        Return the string cluster, entry offeset and the mft entry bytes for the given index

        :param index: int
        :return: tuple(string cluster for the entry: int, offset in the cluster: int, the mft entry bytes: bytes)
        """

        records_in_cluster = int(self.filesystem_reader.get_cluster_size() / self.filesystem_reader.get_record_size())
        cluster_num = int(index / records_in_cluster)
        current_cluster = 0
        # CR: [finish] Parenthesis are not needed
        # CR: [finish] Your names are really confusing. Use cluster_index and
        # current_cluster_index to convey they are numbers.
        for (length, cluster) in self.mft_sectors:
            current_cluster += cluster
            if length > cluster_num:
                current_cluster += cluster_num
                entry_offset = index % records_in_cluster * self.filesystem_reader.get_record_size()
                # CR: [finish] Split to different statements! This will both
                # make this line easier to read, as well as give meaning to its
                # components. You could also break parts into other functions if
                # needed.
                return current_cluster, entry_offset, \
                    self.filesystem_reader.get_cluster(current_cluster)[entry_offset:
                                                                        entry_offset + self.filesystem_reader.get_record_size()]
            else:
                cluster_num -= length
        return None

    # CR: [requirements] Were you required to search the attribute list?
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
        # CR: [design] Way too many nested levels. This must be broken down
        while current_pos < attribute_length:
            # CR: [requirements] Are you allowed to assume endianity
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
        # CR: [finish] Avoid magic numbers
        # CR: [implementation] How about something like:
        # all_attrs = attr_parser.get_attribute_by_id(needed_id) + self._get_atributes_from_attr_list(needed_id)
        # return filter(lambda attribute: attribute is not None, all_attrs)
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

    # CR: [finish] Do not use object names for functions. Objects are
    # something, while functions do something. A fitting name for this one
    # would be get_entry_filenames.
    def filename_parser(self, entry_bytes: bytes, entry_index: int):
        """
        Parse the given mft entry and return the all the names of the file

        :param entry_index: int
        :param entry_bytes: bytes
        :return: filename : list(filenames: str)
        """

        # CR: [finish] Avoid magic numbers
        filename_attributes_bytes = self.attribute_search(entry_bytes, 48, entry_index)
        # CR: [design] Return an empty list
        if len(filename_attributes_bytes) == 0:
            return None

        filenames = []

        for filename_attribute_bytes in filename_attributes_bytes:
            # CR: [design] All the logic here should be encapsulated in an
            # Attribute class
            if filename_attribute_bytes is None:
                return None
            content_offset = int.from_bytes(filename_attribute_bytes[20:21], byteorder='little')
            filename_attribute_bytes = filename_attribute_bytes[content_offset:]
            name_len = int(filename_attribute_bytes[64]) * 2
            # CR: [implementation] Perform decoding correctly
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
