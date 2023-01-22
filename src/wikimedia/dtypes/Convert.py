import pathlib

class Convert:

    def __init__(self, source: pathlib.Path, dest: pathlib.Path, lines: int, dest_pattern: str, log: pathlib.Path):
        """
        Settings for convert process

        Parameters
        ----------
        source : pathlib.Path
            The .xml file sourced from Wikimedia
        dest : pathlib.Path
            The folder for the converted TXT files
        lines: int
            The number of lines per TXT file
        dest_pattern: str
            The format of the TXT file name
        log: pathlib.Path
            The folder of raw XML chunks that did not process
        """
        self._source = source
        self._dest = dest
        self._lines = lines
        self._dest_pattern = dest_pattern
        self._log = log

    @property
    def source(self) -> pathlib.Path:
        return self._source
    @property
    def dest(self) -> pathlib.Path:
        return self._dest
    @property
    def lines(self) -> int:
        return self._lines
    @property
    def dest_pattern(self) -> str:
        return self._dest_pattern
    @property
    def log(self) -> pathlib.Path:
        return self._log

    def validate(self) -> None:
        """
        Ensures the settings have face validity
        """
        def _file(path: pathlib.Path) -> None:
            if not path.exists():
                raise ValueError(f'{str(path)} is does not exist')
            if not path.is_file():
                raise ValueError(f'{str(path)} is not a file')
        def _folder(path: pathlib.Path) -> None:
            if not path.exists():
                raise ValueError(f'{str(path)} is does not exist')
            if not path.is_dir():
                raise ValueError(f'{str(path)} is not a folder')
        def _nonzero_int(val: int):
            if val <= 0:
                raise ValueError(f'{val} must be > 0')
        _file(self._source)
        _folder(self._dest)
        _nonzero_int(self._lines)
        if self._log is not None:
            _folder(self._log)
