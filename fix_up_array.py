from fs_file_reader import FSFileReader


class FixUpArray:

    FIX_UP_SIZE = 2

    def __init__(self, fix_up_array_bytes: bytes, entries_num: int):
        """
        Parse the fixup array and save its values

        :param fix_up_array_bytes: the fix up array bytes to parse
        :param entries_num: number of entries in the array
        """

        self._fixed_value = fix_up_array_bytes[:2]

        self._origin_values = [bytes(value) for value in zip(fix_up_array_bytes[2::2], fix_up_array_bytes[3::2])]

    def replace_fix_ups(self, mft_entry: bytearray) -> bytes:
        """
        Replace the fix ups value in the byte array, if found wrong fix up raise OSError

        :param mft_entry: the mft entry to change the fix ups values
        :return: mft entry without fix ups
        """

        for index, origin_value in enumerate(self._origin_values):
            fix_up_offset = (FSFileReader.SECTOR_SIZE - self.FIX_UP_SIZE) + (FSFileReader.SECTOR_SIZE * index)
            if mft_entry[fix_up_offset: fix_up_offset + self.FIX_UP_SIZE] != self._fixed_value:
                raise OSError
            mft_entry[fix_up_offset: fix_up_offset + 2] = origin_value
        return mft_entry
