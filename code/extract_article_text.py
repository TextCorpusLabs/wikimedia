import html
import mwparserfromhell
import mwxml
import pathlib
import shutil
import progressbar as pb
import typing as t
import utils as u
from argparse import ArgumentParser
from collections import namedtuple
from os.path import getsize
from typeguard import typechecked

# declare all the named tuples up front
WMD = namedtuple('WMD', 'id title paragraphs')

@typechecked
def extract_article_text(mediawiki_file: pathlib.Path, articles_folder: pathlib.Path) -> None:
    """
    Converts a Wikimedia dump file to folder containing all the articles minus any wiki markup.
    Articles that contain no text are removed.
    Disambiguation articles are removed.

    Parameters
    ----------
    mediawiki_file : pathlib.Path
        The XML dump file from Wikimedia
    articles_folder : pathlib.Path
        The folder containing all the articles
    """

    if articles_folder.exists():
        shutil.rmtree(str(articles_folder))
    articles_folder.mkdir(parents = True)

    widgets = ['Extracting Articles: ', pb.Percentage(), ' ', pb.Bar(marker = '.', left = '[', right = ']'), ' ', pb.ETA()]
    with pb.ProgressBar(widgets = widgets, max_value = getsize(mediawiki_file)) as bar:
        with open(mediawiki_file, 'r', encoding = 'utf-8') as mediawiki_file:
            for article in u.list_articles(mediawiki_file):
                try:
                    wmd = __parse_wmd(article)
                    if len(wmd.paragraphs) > 0:
                        __write_article_file(articles_folder, wmd)
                        bar.update(mediawiki_file.tell())
                except Exception as ex:
                    print(article.page.title + ': ' + str(ex))

@typechecked
def __parse_wmd(article: mwxml.iteration.revision.Revision) -> WMD:
    """
    Gets the parts of the wiki markdown we care about
    """

    wikicode = mwparserfromhell.parse(article.text)
    text = ''.join(map(__extract_text, wikicode.nodes))
    paragraphs = __clean_wmd(text)

    return WMD(article.page.id, article.page.title, paragraphs)

@typechecked
def __extract_text(node: mwparserfromhell.nodes.Node) -> str:
    """
    Extracts the text from a wikinode

    There are a lot of cases where wikimarkup has characters that are for programing, not reading.
    We want to prune these out.
    """
    if isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
        return __extract_text_Wikilink(node)
    elif isinstance(node, mwparserfromhell.nodes.text.Text):
        return str(node)
    elif isinstance(node, mwparserfromhell.nodes.tag.Tag):
        return __extract_text_Tag(node)
    elif isinstance(node, mwparserfromhell.nodes.html_entity.HTMLEntity):
        return __extract_text_html(node)
    elif isinstance(node, mwparserfromhell.nodes.template.Template):
        return ''
    elif isinstance(node, mwparserfromhell.nodes.heading.Heading):  
        return ''
    elif isinstance(node, mwparserfromhell.nodes.external_link.ExternalLink):
        return __extract_text_ExternalLink(node)
    elif isinstance(node, mwparserfromhell.nodes.comment.Comment):
        return ''
    elif isinstance(node, mwparserfromhell.nodes.argument.Argument):
        return ''
    else:
        raise Exception('unknown type: ' + str(type(node)) + ' ' + str(node))

@typechecked
def __extract_text_Wikilink(node: mwparserfromhell.nodes.wikilink.Wikilink) -> str:
    """
    Wikilinks come in 2 formats, thumbnails and actual links.
    In the case of thumbnails, if posible pull out the nested caption.
    """
    if node.title.startswith('File:') or node.title.startswith('Image:'):
        if node.text == None:
            return ''
        else:
            return ''.join(filter(lambda x: 'thumb|' not in x, map(__extract_text, node.text.nodes)))
    else:
        return ''.join(map(__extract_text, node.title.nodes))

@typechecked
def __extract_text_ExternalLink(node: mwparserfromhell.nodes.external_link.ExternalLink) -> str:
    if(node.title == None):
        return ''
    else:
        return ''.join(map(__extract_text, node.title.nodes))

@typechecked
def __extract_text_Tag(node: mwparserfromhell.nodes.tag.Tag) -> str:
    if(node.contents == None):
        return ''
    else:
        return ''.join(map(__extract_text, node.contents.nodes))

@typechecked
def __extract_text_html(node: mwparserfromhell.nodes.html_entity.HTMLEntity) -> str:
    return html.unescape(str(node))

@typechecked
def __clean_wmd(text: str) -> list:
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
    lines = __clean_wmd_leading_categories(lines)
    lines = reversed(list(lines))

    return list(lines)

@typechecked
def __clean_wmd_leading_categories(lines: t.Iterator) -> t.Iterator[str]:
    """
    Cleans up any wikimedia 'Category' tags
    """

    has_content = False
    for line in lines:
        if not line.startswith("Category:") or has_content:
            has_content = True
            yield line

def __write_article_file(articles_folder : pathlib.Path, wmd: WMD) -> None:
    """
    Writes the relevant wmd data to disk
    """

    article_file = articles_folder.joinpath(f'{u.fix_id_width(wmd.id)}.txt')
    with open(article_file, 'w', encoding = 'utf-8') as article_file:
        article_file.write(wmd.title)
        for paragraph in wmd.paragraphs:
            article_file.write('\n\n')
            article_file.write(paragraph)
        article_file.write('\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--file-in',
        help = 'The XML dump file from Wikimedia',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the articles',
        type = pathlib.Path,
        required = True)
    args = parser.parse_args()    
    print(f'in: {args.file_in}')
    print(f'out: {args.folder_out}')
    extract_article_text(args.file_in, args.folder_out)
