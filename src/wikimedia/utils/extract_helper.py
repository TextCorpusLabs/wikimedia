import typing as t
import mwxml

def extract_id(root: mwxml.iteration.revision.Revision) -> t.Optional[int]:
    return root.page.id

def extract_title(root: mwxml.iteration.revision.Revision) -> t.Optional[str]:
    return root.page.title
