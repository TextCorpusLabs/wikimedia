import mwxml # type: ignore

def extract_id(root: mwxml.iteration.revision.Revision) -> int | None:
    if root.page is not None:
        return root.page.id

def extract_title(root: mwxml.iteration.revision.Revision) -> str | None:
    if root.page is not None:
        return root.page.title
