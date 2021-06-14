import html
import jsonlines as jl
import mp_boilerplate as mpb
import mwparserfromhell
import mwxml
import pathlib
import typing as t
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def wikimedia_to_jsonl(mediawiki_in: pathlib.Path, jsonl_out: pathlib.Path, sub_process_count: int) -> None:
    """
    Converts a Wikimedia dump file to a JSONL file containing all the articles minus any wiki markup.
    Articles that contain no text are removed.
    Disambiguation articles are removed.

    Parameters
    ----------
    mediawiki_in : pathlib.Path
        The XML dump file from Wikimedia
    jsonl_file : pathlib.Path
        JSONL containing all the wikimedia articles
    sub_process_count : int
        The number of sub processes used to transformation from in to out formats
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = _collect_articles, extract_args = (mediawiki_in),
        transform = _parse_article,
        save = _save_articles_to_jsonl, save_args = (jsonl_out),
        worker_count = sub_process_count,
        show_progress = True)
    worker.start()
    worker.join()

def _collect_articles(mediawiki_in: pathlib.Path) -> t.Iterator[mwxml.iteration.revision.Revision]:
    """
    Gets the full xml of the wiki article
    mediawiki files store a lot of extra history information.
    we only need the latest information
    """

    dis = 'disambiguation'
    qq = 0

    with open(mediawiki_in, 'r', encoding = 'utf-8') as fp:
        dump = mwxml.Dump.from_file(fp)
        for page in dump:
            if qq >= 50000:
                break
            if page.namespace == 0 and page.redirect is None and dis not in page.title:
                last_revision = None
                for revision in page:
                    if not revision.deleted.text:
                        last_revision = revision
                if last_revision is not None and last_revision.model == 'wikitext':
                    yield last_revision

def _parse_article(article: mwxml.iteration.revision.Revision) -> dict:
    """
    Gets the parts of the wiki markdown we care about
    """

    wikicode = mwparserfromhell.parse(article.text)
    text = ''.join(map(_extract_text, wikicode.nodes))
    paragraphs = _clean_article(text)
    json = { 'id' : article.page.id, 'title' : article.page.title, 'text' : paragraphs }

    return json

def _extract_text(node: mwparserfromhell.nodes.Node) -> str:
    """
    Extracts the text from a wikinode

    There are a lot of cases where wikimarkup has characters that are for programing, not reading.
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
    Wikilinks come in 2 formats, thumbnails and actual links.
    In the case of thumbnails, if posible pull out the nested caption.
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

def _clean_article(text: str) -> list:
    """
    Cleans an article text extract

    Normaly a files are read a line, write a line.
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

def _clean_leading_categories(lines: t.Iterator) -> t.Iterator[str]:
    """
    Cleans up any wikimedia 'Category' tags
    """

    has_content = False
    for line in lines:
        if not line.startswith("Category:") or has_content:
            has_content = True
            yield line

def _save_articles_to_jsonl(results: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-8') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                if len(item['text']) > 0:
                    writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--wikimedia-in',
        help = 'The XML dump file from Wikimedia',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'JSONL containing all the wikimedia articles',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-spc', '--sub-process-count',
        help = 'The number of sub processes used to transformation from in to out formats',
        type = int,
        default = 1)
    args = parser.parse_args()
    print(f'wikimedia in: {args.wikimedia_in}')
    print(f'jsonl out: {args.jsonl_out}')
    print(f'sub process count: {args.sub_process_count}')
    wikimedia_to_jsonl(args.wikimedia_in, args.jsonl_out, args.sub_process_count)
