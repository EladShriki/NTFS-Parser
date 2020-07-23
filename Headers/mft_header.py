import struct
from fix_up_array import FixUpArray


class MftHeader:

    FORMAT = r'4xHH12xHH'

    def __init__(self, mft_entry_bytes: bytes):
        """
        Parse the mft header and save info about the entry

        :param mft_entry_bytes: the mft entry bytes to parse
        """

        self._fix_up_array_offset, \
            self._fix_up_array_entries_num, \
            self.attributes_offset, \
            self.allocated_flag = struct.unpack(self.FORMAT, mft_entry_bytes[:struct.calcsize(self.FORMAT)])

        fix_up_array_end = self._fix_up_array_offset + self._fix_up_array_entries_num * 2
        fix_up_array_bytes = mft_entry_bytes[self._fix_up_array_offset: fix_up_array_end]
        self._fix_up_array = FixUpArray(fix_up_array_bytes, self._fix_up_array_entries_num)

    @property
    def is_allocated(self):
        return self.allocated_flag % 2 == 1

    def get_origin_mft_entry_bytes(self, mft_entry_bytes: bytes) -> bytes:
        """
        Replace the fixup value in the entry with the original value

        :param mft_entry_bytes: bytes
        :return: original_mft_entry_bytes: bytes
        """

        return self._fix_up_array.replace_fix_ups(bytearray(mft_entry_bytes))
