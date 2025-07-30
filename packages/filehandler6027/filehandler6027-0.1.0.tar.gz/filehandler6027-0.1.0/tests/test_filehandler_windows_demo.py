"""
Test Case: Verify FileHandler (Modern Mode) on Windows Platform
"""
from filehandler import FileHandler, FileHandleMode

def test_filehandler_windows():
    print("Trying out FileHandler on windows platform...")

    data = {
        'username': 'charliesky',
        'mission': 'celebrate first successful package install!',
        'status': '★ working perfectly!'
    }

    output_file = '~/Documents/celebration_output.txt'
    handler = FileHandler(FileHandleMode.Modern)

    handler.write(output_file, data)
    content = handler.read(output_file)

    print("✔ File content successfully read back:")
    print(content)

    assert content == data, "❌ Mismatch in written and read data"

if __name__ == '__main__':
    test_filehandler_windows()
