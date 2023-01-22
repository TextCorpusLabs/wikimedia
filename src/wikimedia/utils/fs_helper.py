import mwxml
import pathlib
import typing as t

def list_revisions(mediawiki_in: pathlib.Path) -> t.Iterator[mwxml.iteration.revision.Revision]:
    """
    Gets the full xml of the wiki article
    mediawiki files store a lot of extra history information.
    we only need the latest information
    """
    dis = 'disambiguation'
    with open(mediawiki_in, 'r', encoding = 'utf-8') as fp:
        dump = mwxml.Dump.from_file(fp)
        for page in dump:
            if page.namespace == 0 and page.redirect is None and dis not in page.title:
                last_revision = None
                for revision in page:
                    if not revision.deleted.text:
                        last_revision = revision
                if last_revision is not None and last_revision.model == 'wikitext':
                    yield last_revision
