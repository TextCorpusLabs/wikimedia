import typing as t
import mwxml # type: ignore

Article = t.Dict[str, int | str | t.List[str]]
Extractor = t.Callable[[mwxml.iteration.revision.Revision], int | str | t.List[str] | None]
