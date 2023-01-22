import typing as t

class ProcessError(ValueError):

    def __init__(self, document: str, issues: t.List[str]):
        """
        Settings for metadata process

        Parameters
        ----------
        document : str
            The document that could not be processed
        issues : t.List[str]
            The list of reasons the document did not process
        """
        self._document = document
        if issues is None or len(issues) == 0:
            issues = ['Unknown']
        self._issues = issues
        super().__init__(self._issues)

    @property
    def document(self) -> str:
        return self._document
    @property
    def issues(self) -> t.List[str]:
        return self._issues
