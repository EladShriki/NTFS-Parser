import struct


class BootParser(object):

    FORMAT = r'=11xHB34xQ'

    def __init__(self, boot_sector_bytes: bytes):
        """
        Parse the boot sector data and save important values

        :param boot_sector_bytes: boot sector bytes to parse
        """

        self.bytes_per_sector, \
            self.sectors_per_cluster, \
            self.mft_starting_cluster = struct.unpack(self.FORMAT, boot_sector_bytes[:struct.calcsize(self.FORMAT)])

    @property
    def cluster_size_in_bytes(self):
        return self.bytes_per_sector * self.sectors_per_cluster
