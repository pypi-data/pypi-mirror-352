import os
import time
import tempfile
import threading
import logging

class FileWrapper:
    """
    A simple file wrapper to override the 'name' attribute and
    forward all other attributes and methods to the underlying file.
    """
    def __init__(self, file_obj, short_name):
        self._file_obj = file_obj
        self.name = short_name  # Overridden file name (no path)

    def __enter__(self):
        # Support context manager protocol
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # When exiting context, close the underlying file
        self._file_obj.close()

    def __getattr__(self, item):
        """
        Forward all attributes/methods (except 'name')
        to the underlying file object.
        """
        # For example, .read(), .write(), .seek(), .tell(), etc.
        return getattr(self._file_obj, item)

class FolderManager:
    def __init__(self, folder_path, interval_minutes=5, max_file_lifespan_hours=24):
        """
        Initializes the FolderManager instance.

        Args:
            folder_path (str): Path to the folder to manage.
            interval_minutes (int): Interval in minutes to run the cleanup.
            max_file_lifespan_hours (int): Maximum lifespan of a file in hours.
        """
        self.folder_path = folder_path
        self.interval_minutes = interval_minutes
        self.max_file_lifespan_seconds = max_file_lifespan_hours * 3600
        self.running = False
        self.scheduler_thread = None

        # Create the folder if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logging.info(f"Created folder: {folder_path}")

    def list_files(self):
        """
        Retrieves a list of filenames accessible in the managed folder.
        (Ignores subdirectories and only returns regular files.)

        Returns:
            list of str: A list of filenames in the managed folder.
        """
        return [
            (f, None) for f in os.listdir(self.folder_path)
            if os.path.isfile(os.path.join(self.folder_path, f))
        ]

    def create_file(self, suffix=None):
        """
        Creates a temporary file in the managed folder.

        Returns:
            str: Path to the created temporary file.
        """
        temp_file = tempfile.NamedTemporaryFile(dir=self.folder_path, delete=False, suffix=suffix)
        logging.info(f"Created temp file: {temp_file.name}")
        temp_file.close()
        return os.path.basename(temp_file.name)

    def file_path(self, filename):
        """
        Retrieves the full path of a file by its filename.

        Args:
            filename (str): The name of the file to look up.

        Returns:
            str: The full path of the file if it exists, otherwise None.
        """
        file_path = os.path.join(self.folder_path, filename)
        if os.path.isfile(file_path):
            return file_path
        else:
            logging.info(f"File '{filename}' not found in {self.folder_path}.")
            return None

    def load_file(self, filename):
        fname = self.file_path(filename)
        if fname is not None:
            with open(fname, "rb") as f:
                return f.read()

    def cleanup_old_files(self):
        """
        Deletes files in the managed folder that are older than the configured maximum lifespan.
        """
        current_time = time.time()
        for filename in os.listdir(self.folder_path):
            file_path = os.path.join(self.folder_path, filename)
            if os.path.isfile(file_path):
                file_modified_time = os.path.getmtime(file_path)
                if current_time - file_modified_time > self.max_file_lifespan_seconds:
                    try:
                        os.remove(file_path)
                        logging.info(f"Deleted old file: {file_path}")
                    except Exception as e:
                        logging.info(f"Failed to delete {file_path}: {e}")

    def _scheduler(self):
        """
        Internal method to run the cleanup task at regular intervals.
        """
        while self.running:
            self.cleanup_old_files()
            time.sleep(self.interval_minutes * 60)

    def start_watcher(self):
        """
        Starts the scheduler in a separate thread.
        """
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
            self.scheduler_thread.start()
            logging.info("Scheduler started.")

    def stop_watcher(self):
        """
        Stops the scheduler.
        """
        if self.running:
            self.running = False
            if self.scheduler_thread:
                self.scheduler_thread.join()
            logging.info("Scheduler stopped.")

    def open(self, filename_or_extension, mode="r", encoding=None):
        """
        Opens a file in the managed folder for reading or writing.
        If an extension is provided (e.g., ".txt") and mode is "w",
        a new temporary file is created in the folder.

        Args:
            filename_or_extension (str): Either a file name to open or an extension to create a new file.
            mode (str): Mode to open the file (e.g., 'r', 'w').

        Returns:
            FileWrapper: A wrapped file object whose 'name' attribute is just the file's short name.
        """
        # If a new file needs to be created (e.g., ".txt")
        if filename_or_extension.startswith(".") and mode.startswith("w"):
            temp_file = tempfile.NamedTemporaryFile(
                dir=self.folder_path,
                suffix=filename_or_extension,
                delete=False
            )
            # Extract only the short filename
            short_name = os.path.basename(temp_file.name)
            file_path = temp_file.name
            temp_file.close()
        else:
            # Opening an existing file by name
            file_path = self.file_path(filename_or_extension)
            if not file_path:
                raise FileNotFoundError(
                    f"File '{filename_or_extension}' not found in {self.folder_path}."
                )
            short_name = filename_or_extension

        # Open the real file
        real_file_obj = open(file_path, mode, encoding=encoding)

        # Return a FileWrapper so that 'name' is overridden
        return FileWrapper(real_file_obj, short_name)

    # def open(self, filename_or_extension, mode="r"):
    #     """
    #     Opens a file in the managed folder for reading or writing. If an extension is provided, a new file is created.
    #
    #     Args:
    #         filename_or_extension (str): Either a file name to open or an extension to create a new temporary file.
    #         mode (str): Mode to open the file (e.g., 'r', 'w').
    #
    #     Returns:
    #         File object: A file handle opened in the given mode, with its `name` attribute modified to be the file name.
    #     """
    #     # If a new file needs to be created (e.g., ".txt")
    #     if filename_or_extension.startswith(".") and mode == "w":
    #         temp_file = tempfile.NamedTemporaryFile(dir=self.folder_path, suffix=filename_or_extension, delete=False)
    #         file_name = os.path.basename(temp_file.name)  # Extract only the file name
    #         file_path = temp_file.name
    #         temp_file.close()
    #     else:
    #         # If opening an existing file
    #         file_path = self.get_file_path(filename_or_extension)
    #         if not file_path:
    #             raise FileNotFoundError(f"File '{filename_or_extension}' not found in {self.folder_path}.")
    #         file_name = filename_or_extension
    #
    #     # Open the file and wrap it with a modified file-like object
    #     file_obj = open(file_path, mode, encoding="utf-8")
    #     file_obj.name = file_name  # Modify the `name` attribute to contain only the file name
    #     return file_obj


# Example Usage
if __name__ == "__main__":
    # Initialize the FolderManager for a specific folder
    # Cleanup interval: 10 minutes
    # Maximum file lifespan: 12 hours
    folder_manager = FolderManager("managed_temp_folder", interval_minutes=1, max_file_lifespan_hours=12)

    # Start the scheduler in its own thread
    folder_manager.start_watcher()

    with folder_manager.open(".txt", "w") as f:
        f.write("This is a test file.")
        fname = f.name

    with folder_manager.open(fname, "r") as f:
        print(f.read())

    # Main thread can create files while the scheduler runs
    try:
        for _ in range(3):
            fname = folder_manager.create_file(suffix=".txt")
            print(folder_manager.file_path(fname))
            print(fname)

            time.sleep(20)  # Simulate some activity in the main thread
    except KeyboardInterrupt:
        print("Stopping folder manager...")

    # Stop the scheduler before exiting
    folder_manager.stop_watcher()
