import logging
import zlib
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import threading

from peewee import (
    Model, CharField, IntegerField, BlobField,
    SqliteDatabase, AutoField, DateTimeField
)


def is_temp_file(event):
    return event.src_path.endswith('~') or event.src_path.startswith('~') or event.src_path.endswith('.tmp')


# Create an uninitialized database object
db = SqliteDatabase(None)


class FileRevision(Model):
    """
    Represents one row in the file_revisions table.
    """
    id = AutoField()  # Primary key
    file_id = CharField()
    version_number = IntegerField()
    timestamp = DateTimeField()
    content = BlobField()
    previous_version_number = IntegerField(null=True)
    missing_on_disk = IntegerField(default=0)

    # Metadata fields
    user_name = CharField(null=True)
    status = CharField(default="concept")
    version_comment = CharField(null=True)

    class Meta:
        database = db
        table_name = "file_revisions"


class DebounceHandler(FileSystemEventHandler):
    def __init__(self, manager, delay=2.0):
        self.manager = manager
        self.delay = delay
        self.timer = None

    def _scan_now(self):
        self.manager.scan_folder()

    def schedule_scan(self):
        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(self.delay, self._scan_now)
        self.timer.start()

    def on_modified(self, event):
        if event.is_directory or is_temp_file(event):
            return
        # Schedule or reschedule a new scan
        logging.info("File modified")
        self.schedule_scan()

    def on_created(self, event):
        if event.is_directory or is_temp_file(event):
            return
        # Schedule or reschedule a new scan
        logging.info("File created")
        self.schedule_scan()

    def on_deleted(self, event):
        if event.is_directory or is_temp_file(event):
            return
        # Schedule or reschedule a new scan
        logging.info("File deleted")
        self.schedule_scan()


class ImmediateHandler(FileSystemEventHandler):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
    def on_modified(self, event):
        if event.is_directory or is_temp_file(event): return
        logging.info("File modified → scanning immediately")
        self.manager.scan_folder()
    def on_created(self, event):
        if event.is_directory or is_temp_file(event): return
        logging.info("File created → scanning immediately")
        self.manager.scan_folder()
    def on_deleted(self, event):
        if event.is_directory or is_temp_file(event): return
        logging.info("File deleted → scanning immediately")
        self.manager.scan_folder()


class FileManager:
    def __init__(self, db_path, working_dir=None, debounce_delay=2.0):
        """
        :param db_path: Path to the SQLite database file
        :param working_dir: Directory to store the latest uncompressed files (ignored if database_only=True)
        :param debounce_delay: If not None, sets up a debounced file‐watcher with this delay in seconds.
                               Pass None to disable filesystem watching.
        """
        self.db_path = db_path
        self.working_dir = working_dir
        self.database_only = (working_dir is None)

        # Initialize the DB
        db.init(self.db_path, pragmas={'journal_mode': 'wal'}, check_same_thread=False)
        db.connect()
        db.create_tables([FileRevision], safe=True)
        db.close()

        # If filesystem watching is requested and not in database-only mode:
        self.observer = None

    def start_watcher(self, debounce_delay=None):
        self.debounce_delay = debounce_delay

        if not self.database_only:
            os.makedirs(self.working_dir, exist_ok=True)
            if self.debounce_delay is None:
                handler = ImmediateHandler(manager=self)
                self.observer = Observer()
                self.observer.schedule(handler, path=self.working_dir, recursive=False)
                self.observer.start()
                logging.info(f"Started immediate filesystem watcher on '{self.working_dir}'")
            else:
                # Debounced handler as before
                self.debounce_handler = DebounceHandler(manager=self, delay=self.debounce_delay)
                self.observer = Observer()
                self.observer.schedule(self.debounce_handler, path=self.working_dir, recursive=False)
                self.observer.start()
                logging.info(f"Started filesystem watcher on '{self.working_dir}' with debounce={self.debounce_delay}s")

    def stop_watcher(self):
        """
        Stops the filesystem observer if it was started.
        """
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logging.info("Stopped filesystem watcher.")

    # def __init__(self, db_path, working_dir=None):
    #     """
    #     :param db_path: Path to the SQLite database file
    #     :param working_dir: Directory to store the latest uncompressed files (ignored if database_only=True)
    #     :param database_only: If True, do not read/write files on disk at all;
    #                           all file content is stored/retrieved from the database only.
    #     """
    #     self.db_path = db_path
    #     self.working_dir = working_dir
    #     self.database_only = working_dir is None
    #
    #     # Initialize the DB
    #     db.init(self.db_path, pragmas={'journal_mode': 'wal'}, check_same_thread=False)
    #     db.connect()
    #     db.create_tables([FileRevision], safe=True)
    #     db.close()

    # ----------------------------------------------------------------
    # Basic Utilities
    # ----------------------------------------------------------------
    def get_latest_version_number(self, file_id):
        """Return the highest version_number for a given file_id, or 0 if none exists."""
        with db.atomic():
            row = (FileRevision
                   .select()
                   .where(FileRevision.file_id == file_id)
                   .order_by(FileRevision.version_number.desc())
                   .first())
            return row.version_number if row else 0

    def file_exists_in_db(self, file_id):
        """Return True if file_id is present in the DB, else False."""
        with db.atomic():
            return (FileRevision
                    .select()
                    .where(FileRevision.file_id == file_id)
                    .exists())

    # ----------------------------------------------------------------
    # Loading content from DB
    # ----------------------------------------------------------------
    def load_version(self, file_id, version_number):
        """
        Return the content of a specific version (version_number) of file_id,
        as bytes, from the database. If no matching row is found, returns None.
        """
        with db.atomic():
            row = (FileRevision
                   .select()
                   .where((FileRevision.file_id == file_id) &
                          (FileRevision.version_number == version_number))
                   .first())
            if not row:
                return None

            return zlib.decompress(row.content)

    def load_latest_version(self, file_id):
        """
        Return the latest version of file_id as raw bytes, always from the database.
        (If no row is found, return None.)
        """
        with db.atomic():
            row = (FileRevision
                   .select()
                   .where(FileRevision.file_id == file_id)
                   .order_by(FileRevision.version_number.desc())
                   .first())
            if not row:
                return None

            return zlib.decompress(row.content)

    # ----------------------------------------------------------------
    # Saving / Updating
    # ----------------------------------------------------------------
    def save_new_version(self, file_id, content_bytes,
                         previous_version=None,
                         user_name=None,
                         status=None,
                         version_comment=None):
        """
        Creates a new version record in the DB (version_number = latest+1) ONLY IF:
          - the content is different from the latest, OR
          - the status is different from the latest

        If user_name is None or status is None, we copy them from the current latest version
        so the metadata "carries forward" in the history.

        If database_only=False, we also write the uncompressed file to disk.
        """
        with db.atomic():
            # 1) Get the current latest row for this file
            latest_row = (FileRevision
                          .select()
                          .where(FileRevision.file_id == file_id)
                          .order_by(FileRevision.version_number.desc())
                          .first())

            # If there's an existing row, carry forward user_name/status if not supplied
            old_status = None
            old_content = None
            if latest_row:
                if user_name is None:
                    user_name = latest_row.user_name  # carry forward
                if status is None:
                    status = latest_row.status       # carry forward

                # Decompress old content for comparison
                old_content = zlib.decompress(latest_row.content)
                old_status = latest_row.status

            else:
                # brand new file
                if status is None:
                    status = "concept"  # default if no prior row
                # user_name can remain None if not provided

            # 2) Compare content & status
            content_changed = True
            status_changed = True

            if latest_row:
                # Compare new content_bytes with old_content
                content_changed = (content_bytes != old_content)

                # Compare new status with old_status
                status_changed = (status != old_status)

            # If NEITHER changed, do nothing
            if not content_changed and not status_changed:
                logging.info(f"No change in content or status for '{file_id}' => skipping new version.")
                return

            # 3) Otherwise, create a new version
            new_version = self.get_latest_version_number(file_id) + 1
            compressed_data = zlib.compress(content_bytes, level=9)
            now = datetime.now()

            FileRevision.create(
                file_id=file_id,
                version_number=new_version,
                timestamp=now,
                content=compressed_data,
                previous_version_number=previous_version,
                missing_on_disk=0,
                user_name=user_name,
                status=status,
                version_comment=version_comment,
            )

        logging.info(f"Saved {file_id}, version {new_version}, at {now} (prev={previous_version}).")

        # 4) If not in database_only mode, write to disk
        if not self.database_only and self.working_dir:
            os.makedirs(self.working_dir, exist_ok=True)
            file_path = os.path.join(self.working_dir, file_id)
            with open(file_path, "wb") as f:
                f.write(content_bytes)

        return {
            "file_id": file_id,
            "version_number": new_version,
            "user_name": user_name,
            "status": status,
            "version_comment": version_comment,
            "on_disk": 1,
            "timestamp": now
        }

    def revert_to_version(self, file_id, version_number):
        """
        Loads that old version's content from DB, then calls save_new_version
        referencing the old version_number as previous_version.
        """
        old_content = self.load_version(file_id, version_number)
        if old_content is None:
            logging.info(f"No content found for {file_id} version {version_number}.")
            return

        self.save_new_version(file_id, old_content, previous_version=version_number)
        logging.info(f"Reverted '{file_id}' to version {version_number}, saved as latest.")

    # ----------------------------------------------------------------
    # Disk "Erasure" or "Missing" Handling
    # ----------------------------------------------------------------
    def erase_from_disk(self, file_id):
        """
        Sets the latest version's missing_on_disk=1 and removes the file from disk (if exists).
        If database_only=True, just sets missing_on_disk=1 in the DB.
        """
        with db.atomic():
            latest_ver = self.get_latest_version_number(file_id)
            if latest_ver > 0:
                (FileRevision
                 .update({FileRevision.missing_on_disk: 1})
                 .where((FileRevision.file_id == file_id) &
                        (FileRevision.version_number == latest_ver))
                 .execute())

        if not self.database_only and self.working_dir:
            file_path = os.path.join(self.working_dir, file_id)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logging.info(f"Erased file from disk: {file_path}")
        else:
            logging.info(f"Erased '{file_id}' from disk (database_only={self.database_only}), set missing_on_disk=1.")

    # ----------------------------------------------------------------
    # Disk-based methods that do nothing if database_only=True
    # ----------------------------------------------------------------
    def file_path(self, file_id):
        """
        Returns the full path of the file (file_id) on disk, or None if:
          - database_only is True, or
          - the file does not exist in the working directory.
        """
        # If we are in database_only mode, there's no concept of a file on disk
        if self.database_only:
            logging.info(f"file_path_on_disk called, but database_only=True. Returning None.")
            return None

        # If working_dir is not set, we cannot form a disk path
        if not self.working_dir:
            logging.info("No working_dir configured. Cannot determine file path on disk.")
            return None

        # Build the expected path
        path = os.path.join(self.working_dir, file_id)

        # Check if that file actually exists
        if os.path.isfile(path):
            return path
        else:
            logging.info(f"File '{file_id}' not found in {self.working_dir}.")
            return None

    def compare_content_to_db(self, file_id, disk_content):
        """
        Compare 'disk_content' with the latest DB version. Raises an error if database_only=True.
        """
        if self.database_only:
            raise NotImplementedError("compare_content_to_db not applicable in database-only mode.")

        db_content = self.load_latest_version(file_id)
        if db_content is None:
            return True
        return disk_content != db_content

    def scan_folder(self):
        """
        If not database_only, scans folder and creates new versions for changed/new files.
        """
        if self.database_only:
            logging.info("scan_folder() called, but database_only=True. Doing nothing.")
            return

        logging.info("Scanning folder...")
        if not self.working_dir:
            logging.info("No working_dir set, cannot scan.")
            return

        files_on_disk = []
        for entry in os.scandir(self.working_dir):
            if entry.is_file():
                file_id = entry.name
                logging.info(f"  Found file {file_id}")
                files_on_disk.append(file_id)

                with open(entry.path, "rb") as f:
                    disk_content = f.read()

                if not self.file_exists_in_db(file_id):
                    # brand-new
                    self.save_new_version(file_id, disk_content)
                else:
                    # if changed, create new version
                    if self.compare_content_to_db(file_id, disk_content):
                        self.save_new_version(file_id, disk_content)
                    else:
                        self.ensure_not_missing(file_id)

        self.flag_missing_files(files_on_disk)

    def flag_missing_files(self, files_on_disk):
        """
        If not database_only, flags DB file_ids not in 'files_on_disk' as missing_on_disk=1.
        """
        if self.database_only:
            logging.info("flag_missing_files() called, but database_only=True. Doing nothing.")
            return

        with db.atomic():
            all_file_ids = (FileRevision
                            .select(FileRevision.file_id)
                            .distinct())
            for row in all_file_ids:
                fid = row.file_id
                if fid not in files_on_disk:
                    latest_ver = self.get_latest_version_number(fid)
                    updated_count = (
                        FileRevision
                        .update({FileRevision.missing_on_disk: 1})
                        .where(
                            (FileRevision.file_id == fid) &
                            (FileRevision.version_number == latest_ver) &
                            (FileRevision.missing_on_disk == 0)
                        )
                        .execute()
                    )
                    if updated_count > 0:
                        logging.info(f"Flagged '{fid}' (version {latest_ver}) as missing on disk.")

    # ----------------------------------------------------------------
    # Utility for listing files & metadata
    # ----------------------------------------------------------------
    def list_files(self):
        """
        Return a list of (file_id, latest_version_number) for each file whose
        latest revision is not flagged missing_on_disk.
        """
        from peewee import fn

        with db.atomic():
            subquery = (FileRevision
                        .select(
                            FileRevision.file_id,
                            fn.MAX(FileRevision.version_number).alias('max_ver')
                        )
                        .where(FileRevision.missing_on_disk == 0)
                        .group_by(FileRevision.file_id))

            results = []
            for row in subquery.dicts():
                fid = row['file_id']
                max_ver = row['max_ver']
                results.append((fid, max_ver))
            return results

    def ensure_not_missing(self, file_id):
        """
        If not database_only, sets missing_on_disk=0 for the latest version.
        """
        if self.database_only:
            logging.info("ensure_not_missing() called, but database_only=True. Doing nothing.")
            return

        with db.atomic():
            max_ver = self.get_latest_version_number(file_id)
            if max_ver > 0:
                (FileRevision
                 .update({FileRevision.missing_on_disk: 0})
                 .where((FileRevision.file_id == file_id) &
                        (FileRevision.version_number == max_ver))
                 .execute())

    # ----------------------------------------------------------------
    # Pruning & Listing with Metadata
    # ----------------------------------------------------------------
    def prune_by_date(self, cutoff_date: str, keep_latest=True):
        with db.atomic():
            if keep_latest:
                total_deleted = 0
                file_ids = (FileRevision
                            .select(FileRevision.file_id)
                            .distinct())
                for row in file_ids:
                    fid = row.file_id
                    newest = (FileRevision
                              .select(FileRevision.version_number, FileRevision.timestamp)
                              .where(FileRevision.file_id == fid)
                              .order_by(FileRevision.version_number.desc())
                              .first())
                    if not newest:
                        continue
                    delete_q = (FileRevision
                                .delete()
                                .where(
                                    (FileRevision.file_id == fid) &
                                    (FileRevision.timestamp < cutoff_date) &
                                    (FileRevision.version_number != newest.version_number)
                                ))
                    deleted_count = delete_q.execute()
                    total_deleted += deleted_count
                return total_deleted
            else:
                delete_q = FileRevision.delete().where(FileRevision.timestamp < cutoff_date)
                return delete_q.execute()

    def prune_by_count(self, max_versions=5):
        total_deleted = 0
        with db.atomic():
            file_ids = (FileRevision
                        .select(FileRevision.file_id)
                        .distinct())

            for row in file_ids:
                fid = row.file_id
                query_versions = (FileRevision
                                  .select()
                                  .where(FileRevision.file_id == fid)
                                  .order_by(FileRevision.version_number.desc()))
                rows_to_delete = list(query_versions.offset(max_versions))
                if not rows_to_delete:
                    continue

                row_ids = [r.id for r in rows_to_delete]
                delete_q = (FileRevision
                            .delete()
                            .where(FileRevision.id.in_(row_ids)))
                deleted_count = delete_q.execute()
                total_deleted += deleted_count
        return total_deleted

    def list_files_with_metadata(
            self,
            user_name=None,
            status=None,
            available_on_disk=None,
            time_filter=None
    ):
        """
        Return a list of dicts, describing the "latest" version for each file
        valid at the given time_filter. If time_filter is None, treat it as "now."

        You can filter by user_name, status, on-disk status, etc.
        """
        if time_filter is None:
            time_filter = datetime.now()

        with db.atomic():
            distinct_ids = (FileRevision
                            .select(FileRevision.file_id)
                            .where(FileRevision.timestamp <= time_filter)
                            .distinct())

            results = []
            for row in distinct_ids:
                fid = row.file_id
                latest_at_time = (
                    FileRevision
                    .select()
                    .where(
                        (FileRevision.file_id == fid) &
                        (FileRevision.timestamp <= time_filter)
                    )
                    .order_by(FileRevision.timestamp.desc())
                    .first()
                )
                if not latest_at_time:
                    continue

                # Filter checks
                if user_name is not None and latest_at_time.user_name != user_name:
                    continue
                if status is not None and latest_at_time.status != status:
                    continue
                if available_on_disk is True and latest_at_time.missing_on_disk != 0:
                    continue
                if available_on_disk is False and latest_at_time.missing_on_disk != 1:
                    continue


                results.append({
                    "file_id": latest_at_time.file_id,
                    "version_number": latest_at_time.version_number,
                    "user_name": latest_at_time.user_name,
                    "status": latest_at_time.status,
                    "version_comment": latest_at_time.version_comment,
                    "on_disk": (latest_at_time.missing_on_disk == 0),
                    "timestamp": latest_at_time.timestamp.isoformat()
                })

            results.sort(key=lambda r: (r["file_id"], r["timestamp"]))
            return results





if __name__ == "__main__":
    manager = FileManager(db_path="revisions.db", working_dir="my_files")
    manager.scan_folder()

    manager.save_new_version(
        file_id="example.txt",
        content_bytes=b"Hello world",
        user_name="alice",
        status="for approval",
        version_comment="Added introduction section",
    )

    files = manager.list_files_with_metadata(
        user_name="bob",
        status="for approval",
        available_on_disk=True
    )
    for info in files:
        logging.info(info["file_id"], info["version_number"], info["version_comment"])

    manager.prune_by_count(5)
    manager.start_watcher(debounce_delay=1.0)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.stop_watcher()

    logging.info("Stopped watching.")
