"""Backup stuff."""
from spelltinkle.session import Session


class Backup:
    """Object for handling backup of all open files."""
    def __init__(self, session: Session) -> None:
        self.session = session
        self.folder = session.conf.home / 'backup'
        if not self.folder.is_dir():
            self.folder.mkdir()
        self.n = 0
        self.start()

    def start(self) -> None:
        """Main loop.

        Do backup every two minutes and remove too old files every 10 minutes.
        """
        self.session.loop.call_later(120, self.start)

        if self.n > 0:
            self.do_backup()
            if self.n % 5 == 0:
                self.remove_old_files()

        self.n += 1

    def do_backup(self) -> None:
        """Do backup for files that need it."""
        for doc in self.session.docs:
            if doc.path and doc.backup_needed:
                doc._write(self.folder / doc.path.name)
                doc.backup_needed = False

    def remove_old_files(self) -> None:
        """Remove old files.

        If there are more than 100 files in the backup folder then the oldest
        100 will be removed.
        """
        files = [(f.stat().st_ctime, f)  # type: ignore
                 for f in self.folder.glob('*')]
        for t, f in sorted(files)[:-100]:
            f.unlink()
