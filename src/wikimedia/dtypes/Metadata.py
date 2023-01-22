import pathlib

class Metadata:

    def __init__(self, source: pathlib.Path, dest: pathlib.Path, log: pathlib.Path):
        """
        Settings for metadata process

        Parameters
        ----------
        source : pathlib.Path
            The .xml file sourced from Wikimedia
        dest : pathlib.Path
            The CSV file used to store the metadata
        log: pathlib.Path
            The folder of raw XML chunks that did not process
        """
        self._source = source
        self._dest = dest
        self._log = log

    @property
    def source(self) -> pathlib.Path:
        return self._source
    @property
    def dest(self) -> pathlib.Path:
        return self._dest
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
        _file(self._source)
        _folder(self._dest.parent)
        if self._log is not None:
            _folder(self._log)
