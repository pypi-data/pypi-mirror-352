import os
import shutil


def empty_directory(directory: str):
    """Removes all files and subdirectories inside a directory."""
    if not os.path.exists(directory):
        print(f"Directory '{directory}' does not exist.")
        return

    for item in os.scandir(directory):
        try:
            if item.is_dir():
                shutil.rmtree(item.path)
            else:
                os.unlink(item.path)
        except Exception as e:
            print(f"Error deleting {item.path}: {e}")

    print(f"Emptied directory: {directory}")
