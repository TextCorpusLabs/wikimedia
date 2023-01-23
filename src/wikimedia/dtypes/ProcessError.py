import mwxml # type: ignore
import typing as t

class ProcessError(ValueError):

    def __init__(self, document: mwxml.iteration.Revision, issues: t.List[str]):
        """
        Settings for metadata process

        Parameters
        ----------
        document : mwxml.iteration.Revision
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
    def document(self) -> mwxml.iteration.Revision:
        return self._document
    @property
    def issues(self) -> t.List[str]:
        return self._issues
