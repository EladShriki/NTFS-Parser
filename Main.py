import argparse
from mft import MFT
from file import File


def find_file(mft: MFT, filename_to_find: str) -> File:
    """
    Find the wanted file in the mft file, and return the File.
    Raise FileNotFoundError if file isn't in the mft file

    :param mft: mft File object
    :param filename_to_find: name of the wanted file
    :return: File object of the wanted file
    """
    for index in range(mft.mft_max_index):
        mft_entry_bytes = mft.get_mft_entry(index)
        file = File(mft_entry_bytes, index, mft.filesystem_reader)
        for filename in file.file_names:
            if filename == filename_to_find:
                return file
    raise FileNotFoundError


def main(drive_path: str, file_name_to_find: str):

    mft = MFT(drive_path)

    file = find_file(mft, file_name_to_find)
    data = file.get_content()

    print(f'Data size = {len(data)}')
    print(f'Data:\n{data}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Find a file by given filename in the given disk, "
                                                 "and return the file data")
    parser.add_argument("disk_path", help="Path to the Disk", type=str)
    parser.add_argument("filename", help="Filename to find in the disk", type=str)
    args = parser.parse_args()
    main(args.disk_path, args.filename)
