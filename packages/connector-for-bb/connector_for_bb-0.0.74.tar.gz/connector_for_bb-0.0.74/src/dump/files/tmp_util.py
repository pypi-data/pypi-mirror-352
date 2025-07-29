import logging
import os
from tempfile import TemporaryDirectory


class TemporaryFileSystem:
    """
    Temporary directory utils class
    used for data manipulators
    """

    def __init__(self, file_format: str = "csv") -> None:
        self.file_format = file_format
        self._tmp_dir = TemporaryDirectory()
        self._last_path: str

    def __del__(self) -> None:
        """Fallback cleanup (not guaranteed but added as safety net)."""
        self.cleanup()

    def cleanup(self):
        try:
            self._tmp_dir.cleanup()
        except Exception as e:
            logging.info(f"error during tmp dir cleanup: {e}")

    @property
    def tmp_dir(self) -> str:
        return self._tmp_dir.name

    @property
    def files(self) -> list:
        return os.listdir(str(self.tmp_dir))

    @property
    def next_filename(self) -> str:
        number = 0
        avaliable = [int(x.split(".")[0].split("_")[-1]) for x in self.files]
        if len(avaliable) != 0:
            number = max(avaliable) + 1
        return f"data_{number}.{self.file_format}"

    def save_path(self) -> str:
        self._last_path = os.path.join(str(self.tmp_dir), self.next_filename)
        return self._last_path

    @property
    def dir_info(self) -> None:
        """
        Shows temporary directory info
        file - file size in mb
        """
        for file in self.files:
            check_file = os.path.join(self.tmp_dir, file)
            size = os.path.getsize(check_file) / 1024**2
            print(f"{check_file}: {size} mb")
