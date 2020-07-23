import typing
from fs_file_reader import FSFileReader


class Runlists:

    def __init__(self, runlist_bytes: bytes, filesystem_reader: FSFileReader):
        """
        Parse the runlist of the attribute

        :param runlist_bytes: the runlists bytes in the attribute
        :param filesystem_reader: FSFileReader
        """

        self.filesystem_reader = filesystem_reader
        self.runlists = self._runlists_parse(runlist_bytes)

    def _runlists_parse(self, runlist_bytes: bytes) -> typing.List[typing.Tuple[int, int]]:
        """
        Parse the runlists from the given data attribute and return the runlists in tuple

        :param runlist_bytes: the runlists bytes to parse
        :return: runlists tuples (length: int, cluster: int)
        """

        runlists = []

        while runlist_bytes[0] != 0:
            binary_number = bin(runlist_bytes[0])[2:].zfill(8)
            offset = int(binary_number[:4], 2)
            length_size = int(binary_number[4:], 2)
            length = int.from_bytes(bytes(runlist_bytes[1: 1 + length_size]), byteorder='little')
            vcn = int.from_bytes(runlist_bytes[1 + length_size: 1 + length_size + offset], byteorder='little',
                                 signed=True)
            runlists.append((length, vcn))
            runlist_bytes = runlist_bytes[1 + length_size + offset:]

        return runlists

    def get_data(self) -> bytes:
        """
        Build the data from the runlist and return the data

        :return: the attribute data
        """

        current_cluster = 0
        data = bytes()

        for length_in_clusters, starting_cluster in self.runlists:
            current_cluster += starting_cluster
            data += self.filesystem_reader.get_clusters(current_cluster, length_in_clusters)

        return data
