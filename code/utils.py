import mwxml
import typing as t
from typeguard import typechecked

@typechecked
def list_articles(mediawiki_file: t.TextIO) -> t.Iterator[mwxml.iteration.revision.Revision]:
    """
    mediawiki files store a lot of extra history information.
    we only need the latest information
    """

    dis = 'disambiguation'
    dump = mwxml.Dump.from_file(mediawiki_file)

    for page in dump:
        if page.namespace == 0 and page.redirect is None and dis not in page.title:
            last_revision = None
            for revision in page:
                if not revision.deleted.text:
                    last_revision = revision
            if last_revision is not None and last_revision.model == 'wikitext':
                yield last_revision
