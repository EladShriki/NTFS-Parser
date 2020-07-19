

class AttributeHeaderParser(object):
    def __init__(self, attribute_header_data: bytes):
        """
        Parse mft entry and search for attributes in the mft entry

        :param attribute_header_data: bytes
        """

        self.allocated = int.from_bytes(attribute_header_data[22:23], byteorder='little')
        self.attributes_bytes = attribute_header_data[int.from_bytes(attribute_header_data[20:21], byteorder='little'):]

    def get_attribute_by_id(self, needed_id: int):
        """
        Return attribute bytes by given attribute id, if entry isn't allocated or attribute isn't exist return None

        :param needed_id: int
        :return: attribute : bytes
        """

        if self.allocated == 0:
            return None

        attribute_start_index = 0
        attribute_id = int.from_bytes(self.attributes_bytes[:3], byteorder='little')

        while attribute_id != needed_id:
            if attribute_id == 128:
                return None
            attribute_start_index += int.from_bytes(self.attributes_bytes[attribute_start_index + 4: attribute_start_index + 7],
                                                    byteorder='little')
            attribute_id = int.from_bytes(self.attributes_bytes[attribute_start_index: attribute_start_index + 3],
                                          byteorder='little')

        attribute_size = int.from_bytes(self.attributes_bytes[attribute_start_index + 4: attribute_start_index + 7],
                                        byteorder='little')
        return self.attributes_bytes[attribute_start_index: attribute_start_index + attribute_size]
