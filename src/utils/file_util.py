import os


def open_file(file_path, mode='r'):
    try:
        # Open the file using the 'with' function to ensure the file is automatically closed after use
        with open(file_path, mode) as file:
            return file.read().splitlines()
    # Define possible exceptions that could arise from opening the file
    except FileNotFoundError:
        print(f"ERROR: The file {os.path.basename(file_path)} could not be found.")
    except PermissionError:
        print(f"ERROR: You do not have permission to open file {os.path.basename(file_path)}.")
    except IOError:
        print(f"ERROR: There was an I/O error while opening file {os.path.basename(file_path)}.")
    except TypeError:
        print(f"ERROR: Invalid mode specified when opening file {os.path.basename(file_path)}.")
    except UnicodeDecodeError:
        print(f"ERROR: The encoding of file {os.path.basename(file_path)} is not compatible with its characters.")


def write_to_file(file_path, data, mode='w'):
    try:
        # Open the file using the 'open_file' function and attempt to write to the file
        with open_file(file_path, mode) as file:
            file.write(data)
    # Define possible exceptions that could arise from writing to the file
    except PermissionError:
        print(f"ERROR: You do not have permission to modify file: {os.path.basename(file_path)}")
    except FileNotFoundError:
        print(f"ERROR: The file {os.path.basename(file_path)} could not be found.")
    except IOError:
        print(f"ERROR: There was an I/O error while writing to the file {os.path.basename(file_path)}")
    except TypeError:
        print(f"ERROR: The data you are trying to write is not in a compatible format for file {os.path.basename(file_path)}")
    except UnicodeEncodeError:
        print(f"ERROR: The data you are trying to write contains characters that cannot be encoded for file {os.path.basename(file_path)}")


def remove_file(file_path):
    # Attempt to remove the file using the system python function 'os.remove'
    try:
        os.remove(file_path)
        print(f"{os.path.basename(file_path)} has been removed!")
    # Define possible exceptions that could arise from removing the file
    except FileNotFoundError:
        print(f"ERROR: The file: {os.path.basename(file_path)} could not be found.")
    except PermissionError:
        print(f"ERROR: You do not have permissions to remove file: {os.path.basename(file_path)}")
    except IsADirectoryError:
        print(f"ERROR: The path: {os.path.normpath(file_path)} is a directory not a file.")
    except OSError:
        print(f"ERROR: An error occurred while trying to remove file: {os.path.basename(file_path)}")
