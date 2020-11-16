import html
import jsonlines as jl
import mp_boilerplate as mpb
import mwparserfromhell
import mwxml
import pathlib
import progressbar as pb
import typing as t
from argparse import ArgumentParser
from threading import Thread
from typeguard import typechecked


import time


@typechecked
def wikimedia_to_json(mediawiki_in: pathlib.Path, jsonl_out: pathlib.Path) -> None:
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
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.MultiWorker(_parse_wmd)
    worker.start()
    load = Thread(target = _collect_articles, args = (mediawiki_in, worker))
    load.start()
    _save_to_jsonl(worker, jsonl_out)
    load.join()

@typechecked
def _collect_articles(mediawiki_in: pathlib.Path, worker: mpb.MultiWorker) -> None:
    """
    Gets the full xml of the wiki atricle
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
                    worker.add_task(last_revision)
    worker.finished_adding_tasks()

@typechecked
def _parse_wmd(article: mwxml.iteration.revision.Revision) -> dict:
    """
    Gets the parts of the wiki markdown we care about
    """

    wikicode = mwparserfromhell.parse(article.text)
    text = ''.join(map(_extract_text, wikicode.nodes))
    paragraphs = _clean_wmd(text)
    json = { 'id' : article.page.id, 'title' : article.page.title, 'text' : paragraphs }

    return json

@typechecked
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

@typechecked
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

@typechecked
def _extract_text_ExternalLink(node: mwparserfromhell.nodes.external_link.ExternalLink) -> str:
    if(node.title == None):
        return ''
    else:
        return ''.join(map(_extract_text, node.title.nodes))

@typechecked
def _extract_text_Tag(node: mwparserfromhell.nodes.tag.Tag) -> str:
    if(node.contents == None):
        return ''
    else:
        return ''.join(map(_extract_text, node.contents.nodes))

@typechecked
def _extract_text_html(node: mwparserfromhell.nodes.html_entity.HTMLEntity) -> str:
    return html.unescape(str(node))

@typechecked
def _clean_wmd(text: str) -> list:
    """
    Cleans a wmd text extract

    Normaly a files are read a line, write a line.
    However in this case there are cases where we need to know the contents of the line above or below.
    """

    lines = text.splitlines()
    lines = map(lambda line: line.strip(), lines)
    lines = filter(lambda line: line != '', lines)
    lines = filter(lambda line: line.upper() != 'THUMB', lines)
    lines = reversed(list(lines))
    lines = _clean_wmd_leading_categories(lines)
    lines = reversed(list(lines))

    return list(lines)

@typechecked
def _clean_wmd_leading_categories(lines: t.Iterator) -> t.Iterator[str]:
    """
    Cleans up any wikimedia 'Category' tags
    """

    has_content = False
    for line in lines:
        if not line.startswith("Category:") or has_content:
            has_content = True
            yield line

@typechecked
def _save_to_jsonl(worker: mpb.MultiWorker, jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant wmd data to disk
    """

    bar_i = 0
    widgets = [ 'Writeing Articles # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        with open(jsonl_out, 'w', encoding = 'utf-16') as fp:
            with jl.Writer(fp, compact = True, sort_keys = True) as writer:
                for item in worker.get_results():
                    if len(item['text']) > 0:
                        bar_i = bar_i + 1
                        bar.update(bar_i)
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
    args = parser.parse_args()
    print(f'wikimedia in: {args.wikimedia_in}')
    print(f'JSONL out: {args.jsonl_out}')
    wikimedia_to_json(args.wikimedia_in, args.jsonl_out)
