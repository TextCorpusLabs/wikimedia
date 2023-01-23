import html
import mwparserfromhell as parser # type: ignore
import mwxml # type: ignore
import typing as t

def extract_id(revision: mwxml.iteration.Revision) -> int | None:
    if revision.page is not None:
        return revision.page.id

def extract_title(revision: mwxml.iteration.Revision) -> str | None:
    if revision.page is not None:
        return revision.page.title

def extract_text(revision: mwxml.iteration.Revision) -> t.List[str] | None:
    if revision.text is not None:
        wiki_code = parser.parse(revision.text) # type: ignore
        text = ''.join(map(_extract_text, wiki_code.nodes)) # type: ignore
        paragraphs = _clean_article(text)
        return paragraphs

def _extract_text(node: parser.nodes.Node) -> str:
    """
    Extracts the text from a wiki node
    There are a lot of cases where wiki markup has characters that are for programing, not reading.
    We want to prune these out.
    """
    if isinstance(node, parser.nodes.Wikilink):
        return _extract_text_Wikilink(node)
    elif isinstance(node, parser.nodes.Text):
        return str(node)
    elif isinstance(node, parser.nodes.Tag):
        return _extract_text_Tag(node)
    elif isinstance(node, parser.nodes.HTMLEntity):
        return _extract_text_html(node)
    elif isinstance(node, parser.nodes.Template):
        return ''
    elif isinstance(node, parser.nodes.Heading):  
        return ''
    elif isinstance(node, parser.nodes.external_link.ExternalLink):
        return _extract_text_ExternalLink(node)
    elif isinstance(node, parser.nodes.Comment):
        return ''
    elif isinstance(node, parser.nodes.Argument):
        return ''
    else:
        raise Exception('unknown type: ' + str(type(node)) + ' ' + str(node))

def _extract_text_Wikilink(node: parser.nodes.Wikilink) -> str:
    if node.title.startswith('File:') or node.title.startswith('Image:'): # type: ignore
        if node.text is None: # type: ignore
            return ''
        else:
            return ''.join(filter(lambda x: 'thumb|' not in x, map(_extract_text, node.text.nodes))) # type: ignore
    else:
        return ''.join(map(_extract_text, node.title.nodes)) # type: ignore

def _extract_text_ExternalLink(node: parser.nodes.external_link.ExternalLink) -> str:
    if isinstance(node.title, parser.wikicode.Wikicode): # type: ignore
        return ''.join(map(_extract_text, node.title.nodes)) # type: ignore
    else:
        return ''

def _extract_text_Tag(node: parser.nodes.Tag) -> str:
    if isinstance(node.contents, parser.wikicode.Wikicode): # type: ignore
        return ''.join(map(_extract_text, node.contents.nodes)) # type: ignore
    else:
        return ''

def _extract_text_html(node: parser.nodes.html_entity.HTMLEntity) -> str:
    return html.unescape(str(node))

def _clean_article(text: str) -> t.List[str]:
    lines = text.splitlines()
    t1 = map(lambda line: line.strip(), lines)
    t2 = filter(lambda line: line != '', t1)
    t3 = filter(lambda line: line.upper() != 'THUMB', t2)
    lines = list(t3)
    t4 = reversed(lines)
    t5 = _clean_leading_categories(t4)
    lines = list(t5)
    t6 = reversed(lines)
    lines = list(t6)
    return lines

def _clean_leading_categories(lines: t.Iterator[str]) -> t.Iterator[str]:
    has_content = False
    for line in lines:
        if not line.startswith("Category:") or has_content:
            has_content = True
            yield line