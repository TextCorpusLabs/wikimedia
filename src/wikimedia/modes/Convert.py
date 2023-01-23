import pathlib
import shutil
import typing as t
from ..dtypes import Article, Extractor, ProcessError
from ..dtypes import Convert as settings
from .. import utils
from io import TextIOWrapper

class Convert:

    _eos = "!?."

    def __init__(self, settings: settings):
        """
        Extracts the metadata from the corpus.

        Parameters
        ----------
        settings : dtypes.settings.metadata
            The settings for the process
        """
        self._settings = settings

    def init(self) -> None:
        self._settings.validate()
        if self._settings.dest.exists():
            shutil.rmtree(self._settings.dest)
        self._settings.dest.mkdir(parents = True, exist_ok = True)

    def run(self) -> None:
        fields = Convert._field_selection()
        revisions = utils.list_revisions(self._settings.source)
        revisions = utils.progress_overlay(revisions, 'Reading article #')
        articles = utils.extract_articles(revisions, fields, self._log_bad_extract)
        Convert._flatten_and_save(self._file_name, self._settings.lines, articles)

    def _log_bad_extract(self, error: ProcessError) -> None:
        if self._settings.log is None:
            print(f"Error: {','.join(error.issues)}")
        else:
            utils.write_log(self._settings.log, error)

    def _file_name(self, i: int) -> pathlib.Path:
        file_name = self._settings.dest_pattern.format(id = i)
        file_path = self._settings.dest.joinpath(file_name)
        return file_path

    @staticmethod
    def _field_selection() -> t.Dict[str, Extractor]:
        fields: t.Dict[str, Extractor] = {}
        fields['id'] = utils.extract_id
        fields['title'] = utils.extract_title
        fields['text'] = utils.extract_text
        return fields

    @staticmethod
    def _flatten_and_save(file_name: t.Callable[[int], pathlib.Path], count: int, articles: t.Iterator[Article]) -> None:
        fp: TextIOWrapper | None = None
        fp_i: int = 0
        fp_lines: int = 0
        for article in articles:
            if fp is None:
                fp = open(file_name(fp_i), 'w', encoding = 'utf-8')
                fp_i += 1
                fp_lines = 0
            lines = [line for line in Convert._flatten_article(article)]
            fp.writelines((f'{x}\n' for x in lines))
            fp_lines += len(lines) + 1
            if fp_lines >= count:
                fp.close()
                fp = None
            else:
                fp.writelines(['\n'])
        if fp is not None:
            fp.close()

    @staticmethod
    def _flatten_article(article: Article) -> t.Iterator[str]:
        if 'id' in article:
            yield f"--- {article['id']} ---"
            if 'title' in article and article['title'] is not None and isinstance(article['title'], str):
                yield article['title']
            yield ""
            if 'text' in article and article['text'] is not None and isinstance(article['text'], list):
                for paragraph in article['text']:
                    for sentence in Convert._split_sentences(paragraph):
                        yield sentence
                    yield ""

    @staticmethod
    def _split_sentences(text: str) -> t.Iterator[str]:
        words = text.split()
        st: int = 0
        for i in range(0, len(words)-1):
            if words[i][-1] in Convert._eos:
                if words[i+1][0].isupper() or words[i+1][0].isdigit():
                    yield ' '.join(words[st:(i+1)])
                    st = i + 1
        if st < len(words):
            yield ' '.join(words[st:len(text)])

