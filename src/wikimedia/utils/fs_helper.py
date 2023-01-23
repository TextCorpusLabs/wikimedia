import json
import mwxml # type: ignore
import pathlib
import typing as t
import uuid
from ..dtypes import ProcessError

T = t.TypeVar('T')

def list_revisions(mediawiki_in: pathlib.Path) -> t.Iterator[mwxml.iteration.Revision]:
    """
    Gets the full xml of the wiki article
    mediawiki files store a lot of extra history information.
    we only need the latest information
    """
    with open(mediawiki_in, 'r', encoding = 'utf-8') as fp:
        dump = mwxml.Dump.from_file(fp) # type: ignore
        for page in dump: # type: ignore
            page = _as_clean_page(page)
            if page is not None:
                last_revision: mwxml.Revision | None = None
                for revision in page: # type: ignore
                    if isinstance(revision, mwxml.Revision):
                        if revision.deleted is not None:
                            if not revision.deleted.text:
                                last_revision = revision
                if last_revision is not None and last_revision.model == 'wikitext':
                    yield last_revision

def _as_clean_page(page: t.Any) -> mwxml.Page | None:
    if not isinstance(page, mwxml.Page):
        return None
    if page.namespace is None or page.namespace != 0:
        return None
    if page.redirect is not None:
        return None
    if page.title is None or 'disambiguation' in page.title:
        return None
    return page

def write_log(log: pathlib.Path, error: ProcessError) -> None:
    """
    Writes out a message as a single file
    Parameters
    ----------
    log : pathlib.Path
        The folder of raw messages
    error : ProcessError
        The error itself
    """
    issue = ''.join([tok.capitalize() for tok in error.issues[0].split(' ')])
    path = log.joinpath(f'wikimedia.{issue}.{uuid.uuid4()}.json')
    with open(path, 'w', encoding = 'utf-8', newline = '') as fp:
        if error.document is None:
            fp.write('Missing whole document')
        else:
            fp.write(json.dumps(error.document.to_json()))
