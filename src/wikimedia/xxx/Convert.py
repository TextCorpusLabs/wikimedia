import html
import jsonlines as jl
import mwparserfromhell
import mwxml
import pathlib
import progressbar as pb
import typing as t
from ..modes import const

Article = t.Dict[str, t.Union[int, str, t.List[str]]]

def main(source: pathlib.Path, dest: pathlib.Path, dest_pattern: str, count: int) -> None:
    """
    Converts a Wikimedia dump file to a JSONL file containing all the articles minus any wiki markup.
    Articles that contain no text are removed.
    Disambiguation articles are removed.

    Parameters
    ----------
    source : pathlib.Path
        The root folder of the folders containing JATS files
    dest : pathlib.Path
        The folder to store the converted JSON files
    dest_pattern: str
        The format of the JSON file name
    count : int
        The number of MXML files in a single JSON file
    """
    articles_raw = _collect_articles(source)
    articles = (_parse_article(raw) for raw in articles_raw)
    articles = _save_articles(dest, dest_pattern, count, articles)
    articles = _progress_bar(articles)
    for _ in articles: pass

def _collect_articles(mediawiki_in: pathlib.Path) -> t.Iterator[mwxml.iteration.revision.Revision]:
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

def _parse_article(article: mwxml.iteration.revision.Revision) -> Article:
    """
    Gets the parts of the wiki markdown we care about
    """
    wiki_code = mwparserfromhell.parse(article.text)
    text = ''.join(map(_extract_text, wiki_code.nodes))
    paragraphs = _clean_article(text)
    json = { 'id' : article.page.id, 'title' : article.page.title, 'text' : paragraphs }
    return json

def _extract_text(node: mwparserfromhell.nodes.Node) -> str:
    """
    Extracts the text from a wiki node

    There are a lot of cases where wiki markup has characters that are for programing, not reading.
    We want to prune these out.
    """
    if isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
        return _extract_text_Wikilink(node)
    elif isinstance(node, mwparserfromhell.nodes.text.Text):
        return str(node)
    elif isinstance(node, mwparserfromhell.nodes.tag.Tag):
        return _extract_text_Tag(node)
    elif isinstance(node, mwparserfromhell.nodes.html_entity.HTMLEntity):
        return _extract_text_html(node)
    elif isinstance(node, mwparserfromhell.nodes.template.Template):
        return ''
    elif isinstance(node, mwparserfromhell.nodes.heading.Heading):  
        return ''
    elif isinstance(node, mwparserfromhell.nodes.external_link.ExternalLink):
        return _extract_text_ExternalLink(node)
    elif isinstance(node, mwparserfromhell.nodes.comment.Comment):
        return ''
    elif isinstance(node, mwparserfromhell.nodes.argument.Argument):
        return ''
    else:
        raise Exception('unknown type: ' + str(type(node)) + ' ' + str(node))

def _extract_text_Wikilink(node: mwparserfromhell.nodes.wikilink.Wikilink) -> str:
    """
    Wiki links come in 2 formats, thumbnails and actual links.
    In the case of thumbnails, if possible pull out the nested caption.
    """
    if node.title.startswith('File:') or node.title.startswith('Image:'):
        if node.text == None:
            return ''
        else:
            return ''.join(filter(lambda x: 'thumb|' not in x, map(_extract_text, node.text.nodes)))
    else:
        return ''.join(map(_extract_text, node.title.nodes))

def _extract_text_ExternalLink(node: mwparserfromhell.nodes.external_link.ExternalLink) -> str:
    if(node.title == None):
        return ''
    else:
        return ''.join(map(_extract_text, node.title.nodes))

def _extract_text_Tag(node: mwparserfromhell.nodes.tag.Tag) -> str:
    if(node.contents == None):
        return ''
    else:
        return ''.join(map(_extract_text, node.contents.nodes))

def _extract_text_html(node: mwparserfromhell.nodes.html_entity.HTMLEntity) -> str:
    return html.unescape(str(node))

def _clean_article(text: str) -> list[str]:
    """
    Cleans an article text extract

    Normally a files are read a line, write a line.
    However in this case there are cases where we need to know the contents of the line above or below.
    """
    lines = text.splitlines()
    lines = map(lambda line: line.strip(), lines)
    lines = filter(lambda line: line != '', lines)
    lines = filter(lambda line: line.upper() != 'THUMB', lines)
    lines = reversed(list(lines))
    lines = _clean_leading_categories(lines)
    lines = reversed(list(lines))
    return list(lines)

def _clean_leading_categories(lines: t.Iterator[str]) -> t.Iterator[str]:
    """
    Cleans up any wikimedia 'Category' tags
    """
    has_content = False
    for line in lines:
        if not line.startswith("Category:") or has_content:
            has_content = True
            yield line

def _save_articles(folder_out: pathlib.Path, pattern: str, count: int, articles: t.Iterator[Article]) -> t.Iterator[Article]:
    """
    Writes the relevant data to disk
    """
    fp = None
    writer: jl.Writer = None
    fp_i = 0
    fp_articles = 0
    for article in articles:
        if fp is None:
            fp_name = folder_out.joinpath(pattern.format(id = fp_i))
            fp = open(fp_name, 'w', encoding = 'utf-8', buffering = const.BUFFER_SIZE)
            writer = jl.Writer(fp, compact = True, sort_keys = True)
            fp_articles = 0
        if 'text' in article and len(article['text']) > 0:
            writer.write(article)
            fp_articles = fp_articles + 1
            yield article
        if fp_articles >= count:
            writer.close()
            fp.close()
            writer = None
            fp = None
            fp_i = fp_i + 1
    if fp is not None:
        writer.close()
        fp.close()

def _progress_bar(articles: t.Iterable[Article]) -> t.Iterator[Article]:
    bar_i = 0
    widgets = ['Processing Articles # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for article in articles:
            bar_i = bar_i + 1
            bar.update(bar_i)
            yield article
