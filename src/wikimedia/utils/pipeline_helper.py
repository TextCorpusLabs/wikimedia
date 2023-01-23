import mwxml # type: ignore
import typing as t
from ..dtypes import Article, Extractor, ProcessError

def extract_articles(revisions: t.Iterator[mwxml.iteration.Revision], fields: t.Dict[str, Extractor], log: t.Callable[[ProcessError], None]) -> t.Iterator[Article]:
    """
    Extracts an article's named fields from the string representation
    """
    for revision in revisions:
        try:
            yield _extract_article(revision, fields)
        except ProcessError as error:
            log(error)

def _extract_article(revision: mwxml.iteration.Revision, fields: t.Dict[str, Extractor]) -> Article:
    article: Article = {}
    fails: t.List[str] = []
    for name, extractor in fields.items():
        try:
            value = extractor(revision)
            if value is not None:
                article[name] = value
        except:
            fails.append(name)
    if len(fails) > 0:
        raise ProcessError(revision, [f'Failure {name}' for name in fails])
    return article
