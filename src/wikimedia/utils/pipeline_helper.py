import mwxml # type: ignore
import typing as t
from ..dtypes import Article, Extractor, ProcessError

def extract_articles(documents: t.Iterator[mwxml.iteration.revision.Revision], fields: t.Dict[str, Extractor], log: t.Callable[[ProcessError], None]) -> t.Iterator[Article]:
    """
    Extracts an article's named fields from the string representation
    """
    for document in documents:
        try:
            yield _extract_article(document, fields)
        except ProcessError as error:
            log(error)

def _extract_article(revision: mwxml.iteration.revision.Revision, fields: t.Dict[str, Extractor]) -> Article:
    article: Article = {}
    missing: t.List[str] = []
    for name, extractor in fields.items():
        try:
            value = extractor(revision)
            if value is not None:
                article[name] = value
        except:
            missing.append(name)
    if len(missing) > 0:
        raise ProcessError(revision, [f'Missing {name}' for name in missing])
    return article
