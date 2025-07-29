from pathlib import Path

class FileSystemConnector:
    """Connector to ingest files from a specified folder."""
    def __init__(self, config):
        # Expects config object with a folder_path attribute
        self.folder_path = Path(config.folder_path)
        print(f"Initializing FileSystemConnector for path: {self.folder_path.resolve()}")
        if not self.folder_path.is_dir():
            print(f"Warning: Folder path {self.folder_path} does not exist or is not a directory.")
            # Consider raising an error or creating the directory
            # self.folder_path.mkdir(parents=True, exist_ok=True)

    def ingest(self):
        """Simulates ingesting files from the folder."""
        print(f"FileSystemConnector: Checking folder {self.folder_path} for files...")
        if not self.folder_path.is_dir():
            print(f"Error: Folder {self.folder_path} not found.")
            return

        # Example: yield info about files found
        for item in self.folder_path.iterdir():
            if item.is_file():
                yield {"type": "file", "path": str(item), "name": item.name}

        print(f"FileSystemConnector: Finished checking folder {self.folder_path}.")
