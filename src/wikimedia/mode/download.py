import pathlib
import wget


def main(wiki: str, date: str, dest_folder: pathlib.Path) -> None:
    """
    Downloads the article file associated with a wikimedia data dump

    Parameters
    ----------
    wiki : str
        The wiki's short name. I.E. enwiki
    date : str
        The date the backup snapshot was taken in yyyyMMdd format
    dest_folder : pathlib.Path
        The destination location to use when saving the files
    """

    pages_url = f'https://dumps.wikimedia.org/{wiki}/{date}/{wiki}-{date}-pages-articles-multistream.xml.bz2'
    pages_file = dest_folder.joinpath(f'{wiki}-{date}.xml.bz2')

    wget.download(pages_url, str(pages_file))
