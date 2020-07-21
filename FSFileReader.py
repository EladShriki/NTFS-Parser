

class BootParser(object):
    def __init__(self, boot_sector_bytes: bytes):
        """
        Parse the boot sector data and save important values

        :param boot_sector_bytes: bytes
        """

        # CR: [finish] Magic numbers, magic numbers everywhere...
        self.bytes_per_sector = int.from_bytes(boot_sector_bytes[11:13], byteorder='little')
        self.sectors_per_cluster = int(boot_sector_bytes[13])
        self.mft_start = int.from_bytes(boot_sector_bytes[48:56], byteorder='little')
        # CR: [finish] Break this statement in a way a human can understand the
        # logic.
        self.bytes_per_record = 2**(256 - boot_sector_bytes[64]) if boot_sector_bytes[64] > 127 \
            else (boot_sector_bytes[64] * self.sectors_per_cluster * self.bytes_per_sector)
        self.bytes_per_cluster = self.bytes_per_sector * self.sectors_per_cluster


class FSFileReader(object):
    def __init__(self, fs_file_path):
        """
        Create a FileHandler that contains data about the drive and can read data from the drive

        :param fs_file_path: str
        """

        self.fs_file_path = fs_file_path
        # CR: [design] Catching and quitting is the wrong behavior. If this was
        # a library, then someone using it might have his program terminated.
        # In general, you should let exceptions propagate unless you have a way
        # to handle it gracefully and return valid output.
        try:
            with open(self.fs_file_path, 'rb') as file_system:
                # CR: [finish] Avoid magic numbers. Also it should be 512
                self.boot_data = BootParser(file_system.read(510))
        except FileNotFoundError:
            print("File is not found!")
            quit()

    # CR: [performance] This is probably very inefficient by itself
    # CR: [finish] Avoid code duplication by calling get_data_chunk
    def get_cluster(self, index: int):
        """
        Return the bytes of the wanted cluster

        :param index: int
        :return: cluster_bytes: bytes
        """

        with open(self.fs_file_path, 'rb') as file_system:
            file_system.seek(index * self.boot_data.bytes_per_cluster)
            return file_system.read(self.boot_data.bytes_per_sector * self.boot_data.sectors_per_cluster)

    # CR: [finish] This is not get_data_chunk, this is get_clusters. Also you
    # should use length_in_clusters for clarification.
    def get_data_chunk(self, starting_cluster: int, length: int):
        """
        Read the runlist data from the drive and return the data read

        :param starting_cluster: int
        :param length: int
        :return: runlist_data: bytes
        """

        with open(self.fs_file_path, 'rb') as file_system:
            file_system.seek(starting_cluster * self.boot_data.bytes_per_cluster)
            return file_system.read(length * self.boot_data.bytes_per_cluster)

    def get_record_size(self):
        """
        Return the size of mft entry

        :return: mft_entry_size : int
        """

        return self.boot_data.bytes_per_record

    def get_cluster_size(self):
        """
        Return the size of cluster in bytes

        :return: cluster_size: int
        """

        return self.boot_data.bytes_per_cluster
