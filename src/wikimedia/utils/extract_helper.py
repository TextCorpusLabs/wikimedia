import mwxml # type: ignore

def extract_id(revision: mwxml.iteration.revision.Revision) -> int | None:
    if revision.page is not None:
        return revision.page.id

def extract_title(revision: mwxml.iteration.revision.Revision) -> str | None:
    if revision.page is not None:
        return revision.page.title
