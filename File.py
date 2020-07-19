from FSFileReader import FSFileReader
from AttributeHeaderParser import AttributeHeaderParser
from DataAttributeParser import data_parser


class File(object):
    def __init__(self, filename: str, entry_offset: int, starting_cluster: int, filesystem_reader: FSFileReader):
        """
        File object, save info about the file

        :param filename: str
        :param entry_offset: int
        :param starting_cluster: int
        :param filesystem_reader: FSFileReader
        """

        self.file_name = filename
        self.starting_cluster = starting_cluster
        self.entry_offset = entry_offset
        self.filesystem_reader = filesystem_reader

    def get_content(self):
        """
        Read the current file data with the data parser and return the file data

        :return: file_data : bytes
        """

        entry_bytes = self.filesystem_reader.get_cluster(self.starting_cluster)
        entry_bytes = entry_bytes[self.entry_offset: self.entry_offset + self.filesystem_reader.get_record_size()]
        attribute_parser = AttributeHeaderParser(entry_bytes)
        data_attr = attribute_parser.get_attribute_by_id(128)
        content = data_parser(data_attr, self.filesystem_reader)
        return content


