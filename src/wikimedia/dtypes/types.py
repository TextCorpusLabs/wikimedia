import typing as t
import mwxml

Article = t.Dict[str, t.Union[int, str, t.List[str]]]
Extractor = t.Callable[[mwxml.iteration.revision.Revision], t.Union[int, str, t.List[str]]]
