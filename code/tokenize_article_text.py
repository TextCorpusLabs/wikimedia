import pathlib
import shutil
import progressbar as pb
import typing as t
from argparse import ArgumentParser
from nltk.tokenize import word_tokenize, sent_tokenize
from typeguard import typechecked

@typechecked
def tokenize_article_text(articles_folder: pathlib.Path, tokenized_folder: pathlib.Path) -> None:
    """
    Tokenizes all the articles into the standard form: one sentence per line, paragraphs have a blank line between them.

    Parameters
    ----------
    articles_folder : pathlib.Path
        The folder containing all the articles
    tokenized_folder : pathlib.Path
        The folder containing all the articles after tokenization
    """

    if tokenized_folder.exists():
        shutil.rmtree(str(tokenized_folder))
    tokenized_folder.mkdir(parents = True)

    bar_i = 1
    widgets = [ 'Tokenizing Article # ', pb.Counter(), ' ', pb.Timer(), ' ', pb.BouncingBar(marker = '.', left = '[', right = ']')]
    with pb.ProgressBar(widgets = widgets) as bar:
        for file_name in articles_folder.iterdir():
            if file_name.is_file() and file_name.suffix.lower() == '.txt' and not file_name.stem.startswith('_'):
                bar.update(bar_i)
                bar_i = bar_i + 1
                with open(file_name, 'r', encoding = 'utf-8') as article:
                    lines = article.readlines()
                lines = __tokenize_lines(lines)
                __write_article_file(tokenized_folder, file_name, lines)

@typechecked
def __tokenize_lines(lines: list) -> t.Iterator[str]:
    """
    Tokenizes all the lines into paragraphs/words using standard Punkt + Penn Treebank tokenizers
    Due to how Wikimedia articales were extracted in the prior step, 1 line = 1 paragraph
    """

    for line in lines:
        line = line.strip()
        if line == '':
            yield ''
        else:
            sentences = sent_tokenize(line)
            for sentence in sentences:
                words = word_tokenize(sentence)
                yield ' '.join(words)

@typechecked
def __write_article_file(tokenized_folder: pathlib.Path, article_file:  pathlib.Path, lines: t.Iterator[str]) -> None:
    file_out = tokenized_folder.joinpath(article_file.name)
    with open(file_out, 'w', encoding = 'utf-8') as file_out:
        for line in lines:
            file_out.write(f'{line}\n')

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--folder-in',
        help = 'The folder containing all the articles',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--folder-out',
        help = 'The folder containing all the articles after tokenization',
        type = pathlib.Path,
        required = True)
    args = parser.parse_args()    
    print(f'in: {args.folder_in}')
    print(f'out: {args.folder_out}')
    tokenize_article_text(args.folder_in, args.folder_out)
