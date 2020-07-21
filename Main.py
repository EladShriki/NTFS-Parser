from MFT import MFT

# CR: [bug] Not sure what the first input should be, but providing \\.\C:
# caused it to crash.

# CR: [performance] How much time does it take to retrieve files?

# CR: [design] Let's talk about OOP
# CR: [design] Let's talk about cleaning up parsing functions

# CR: [general] Let's talk about packages
# CR: [conventions] Modules in python (= files) should be lower snake case
# CR: [conventions] Sort imports by decreasing length
# CR: [conventions] Limit lines to 80 characters
# CR: [conventions] Private methods and members should start with '_'
# CR: [conventions] Methods should appear in the order they're used (top down)
# CR: [finish] If you're using type hints, I recommend using them for return
# values as well with the -> syntax.

# CR: [finish] Docstrings should provide information to end users.
# If they do not do so they should not exist. Specifying parameter types in
# docstrings is nice, but redundant when using type hints and may lead to
# conflicts. The main purpose of specifying parameters is to explain their
# meaning, not their type.


def main():

    # CR: [implementation] Don't make interactive utilities if possible. Use
    # argparse to parse command line arguments instead.
    # CR: [requirements] Were you asked to operate on .dd files?
    dd_file = input("Enter path to the .dd file:")
    mft = MFT(dd_file)
    print("File read successfully!")
    files = mft.get_files_dict()

    # CR: [requirements] Were you asked to run in a loop?
    # CR: [implementation] There's no clean way to exit this loop
    while True:
        filename = input("Enter file name:")
        file = files.get(filename)
        if file is None:
            print('No such a file!')
            continue
        data = file.get_content()
        print(f'Data size = {len(data)}')
        print(f'Data:\n{data}')
        # CR: [finish] What is this good for?
        del data


if __name__ == '__main__':
    main()
