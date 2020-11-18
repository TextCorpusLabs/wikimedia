import pathlib
import jsonlines as jl
import mp_boilerplate as mpb
import typing as t
from argparse import ArgumentParser
from nltk.tokenize import word_tokenize, sent_tokenize
from typeguard import typechecked

@typechecked
def tokenize_wikimedia_jsonl(jsonl_in: pathlib.Path, jsonl_out: pathlib.Path) -> None:
    """
    Tokenizes all the articles into the standard form: one sentence per line, paragraphs have a blank line between them.

    Parameters
    ----------
    jsonl_in : pathlib.Path
        The JSONL containing all the articles
    jsonl_out : pathlib.Path
        The JSONL containing all the articles after tokenization
    """

    if jsonl_out.exists():
        jsonl_out.unlink()

    worker = mpb.EPTS(
        extract = _collect_articles, extract_args = (jsonl_in),
        transform = _tokenize_article,
        save = _save_articles_to_jsonl, save_args = (jsonl_out),
        show_progress = True)
    worker.start()
    worker.join()

def _collect_articles(jsonl_in: pathlib.Path) -> t.Iterator[dict]:
    with open(jsonl_in, 'r', encoding = 'utf-16') as fp:
        with jl.Reader(fp) as reader:
            for item in reader:
                yield item

def _tokenize_article(article: dict) -> dict:
    lines = [line for line in _tokenize_lines(article['text'])]
    json = { 'id' : article['id'], 'title' : article['title'], 'text': article['text'], 'tokenized' : lines }
    return json

def _tokenize_lines(lines: t.List[str]) -> t.Iterator[str]:
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

def _save_articles_to_jsonl(results: t.Iterator[dict], jsonl_out: pathlib.Path) -> None:
    """
    Writes the relevant data to disk
    """
    with open(jsonl_out, 'w', encoding = 'utf-16') as fp:
        with jl.Writer(fp, compact = True, sort_keys = True) as writer:
            for item in results:
                writer.write(item)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-in', '--jsonl-in',
        help = 'The JSONL containing all the articles',
        type = pathlib.Path,
        required = True)
    parser.add_argument(
        '-out', '--jsonl-out',
        help = 'The JSONL containing all the articles after tokenization',
        type = pathlib.Path,
        required = True)
    args = parser.parse_args()    
    print(f'in: {args.jsonl_in}')
    print(f'out: {args.jsonl_out}')
    tokenize_wikimedia_jsonl(args.jsonl_in, args.jsonl_out)
