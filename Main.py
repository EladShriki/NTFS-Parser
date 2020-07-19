from MFT import MFT


def main():

    dd_file = input("Enter path to the .dd file:")
    mft = MFT(dd_file)
    print("File read successfully!")
    files = mft.get_files_dict()

    while True:
        filename = input("Enter file name:")
        file = files.get(filename)
        if file is None:
            print('No such a file!')
            continue
        data = file.get_content()
        print(f'Data size = {len(data)}')
        print(f'Data:\n{data}')
        del data


if __name__ == '__main__':
    main()
