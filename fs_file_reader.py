from boot_parser import BootParser


class FSFileReader(object):

    SECTOR_SIZE = 512

    def __init__(self, fs_file_path):
        """
        Create a FileHandler that contains data about the drive and can read data from the drive

        :param fs_file_path: filesystem path
        """

        self._fs_file_path = fs_file_path
        with open(self._fs_file_path, 'rb') as file_system:
            self._boot_data = BootParser(file_system.read(self.SECTOR_SIZE))

    def get_clusters(self, starting_cluster: int, length_in_clusters: int) -> bytes:
        """
        Read the runlist data from the drive and return the data read

        :param starting_cluster: the starting cluster to read from
        :param length_in_clusters: the number of cluster to read
        :return: runlist_data: the bytes read from all the clusters
        """

        with open(self._fs_file_path, 'rb') as file_system:
            file_system.seek(starting_cluster * self._boot_data.cluster_size_in_bytes)
            return file_system.read(length_in_clusters * self._boot_data.cluster_size_in_bytes)

    @property
    def cluster_size(self):
        return self._boot_data.cluster_size_in_bytes

    # CR: [design] This doesn't seem to belong here...
    @property
    def mft_starting_cluster(self):
        return self._boot_data.mft_starting_cluster
