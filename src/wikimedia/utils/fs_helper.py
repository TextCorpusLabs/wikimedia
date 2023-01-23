import mwxml # type: ignore
import pathlib
import typing as t
import uuid
from ..dtypes import ProcessError

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
    path = log.joinpath(f'wikimedia.{issue}.{uuid.uuid4()}.xml')
    with open(path, 'w', encoding = 'utf-8', newline = '') as fp:
        fp.write(error.document)
