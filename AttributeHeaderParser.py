

class AttributeHeaderParser(object):
    def __init__(self, attribute_header_data: bytes):
        """
        Parse mft entry and search for attributes in the mft entry

        :param attribute_header_data: bytes
        """

        self.allocated = int.from_bytes(attribute_header_data[22:23], byteorder='little')
        self.attributes_bytes = attribute_header_data[int.from_bytes(attribute_header_data[20:21], byteorder='little'):]
        self.entry_size = int.from_bytes(attribute_header_data[24:27], byteorder='little')

    def get_attribute_by_id(self, needed_id: int):
        """
        Return all attribute bytes by given attribute id, if entry isn't allocated or attribute isn't exist return None

        :param needed_id: int
        :return: attribute : list(bytes)
        """

        if self.allocated == 0:
            return None

        attributes = []
        attribute_start_index = 0
        attribute_id = int.from_bytes(self.attributes_bytes[:3], byteorder='little')

        while attribute_id != -1:

            if attribute_id == needed_id:
                attribute_size = int.from_bytes(
                    self.attributes_bytes[attribute_start_index + 4: attribute_start_index + 7], byteorder='little')
                attributes.append(self.attributes_bytes[attribute_start_index: attribute_start_index + attribute_size])

            attribute_start_index += int.from_bytes(self.attributes_bytes[attribute_start_index + 4: attribute_start_index + 7],
                                                    byteorder='little')
            attribute_id = int.from_bytes(self.attributes_bytes[attribute_start_index: attribute_start_index + 3],
                                          byteorder='little', signed=True)

        return attributes

