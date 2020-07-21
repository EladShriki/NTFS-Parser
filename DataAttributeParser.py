from FSFileReader import FSFileReader


# CR: [design] Why not group things into a class that can hold state?

def resident_parse(data_attribute: bytes):
    """
    Read the resident data from the given data attribute and return that data

    :param data_attribute: bytes
    :return: file data: bytes
    """

    data_size = int.from_bytes(data_attribute[16:19], byteorder='little')
    data_offset = int.from_bytes(data_attribute[20:21], byteorder='little')
    return data_attribute[data_offset: data_offset + data_size]


def runlists_parse(data_attributes: bytes):
    """
    Parse the runlists from the given data attribute and return the runlists in tuple

    :param data_attributes: bytes
    :return: runlist tuple (length: int, cluster: int)
    """

    runlists = []
    runlist_offset = int.from_bytes(data_attributes[32:33], byteorder='little')
    data_attributes = data_attributes[runlist_offset:]

    while data_attributes[0] != 0:
        offset = int(bin(data_attributes[0])[:4], 2)
        length_size = int(bin(data_attributes[0])[4:], 2)
        length = int.from_bytes(bytes(data_attributes[1: 1 + length_size]), byteorder='little')
        # CR: [finish] Local variables should be lower snake case
        VCN = int.from_bytes(data_attributes[1 + length_size: 1 + length_size + offset], byteorder='little', signed=True)
        runlists.append((length, VCN))
        data_attributes = data_attributes[1 + length_size + offset:]

    return runlists


def get_data_size(data_attribute: bytes):
    """
    Return the size of the file data

    :param data_attribute:
    :return: file_data_size : int
    """

    return int.from_bytes(data_attribute[48:55], byteorder='little')


def data_builder(runlists, filesystem: FSFileReader):
    """
    Build the file data from the given runlists and return the combined data

    :param runlists: tuple (length: int, cluster: int)
    :param filesystem: FSFileReader
    :return: file_data : bytes
    """

    current_cluster = 0
    data = bytes()
    for (length, cluster) in runlists:
        current_cluster += cluster
        data += filesystem.get_data_chunk(current_cluster, length)

    return data


def data_parser(data_attribute: bytes, filesystem: FSFileReader):
    """
    Parse given data attribute and return the file data

    :param data_attribute: bytes
    :param filesystem: FSFileReader
    :return: file_data : bytes
    """

    # CR: [finish] If you're writing comments, your code isn't clear enough
    if data_attribute[8]:  # Check if resident
        file_size = int.from_bytes(data_attribute[48: 55], byteorder='little')
        runlists = runlists_parse(data_attribute)
        return data_builder(runlists, filesystem)[:file_size]
    else:
        return resident_parse(data_attribute)

