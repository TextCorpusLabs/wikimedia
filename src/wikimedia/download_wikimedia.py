import pathlib
import sys
import wget
from argparse import ArgumentParser
from typeguard import typechecked

@typechecked
def download_wikimedia(wiki: str, date: str, dest_folder: pathlib.Path) -> None:
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
    
@typechecked
def writable_folder(folder_path: str) -> pathlib.Path:
    folder_path = pathlib.Path(folder_path).resolve()
    if not folder_path.exists():
        folder_path.mkdir(parents = True)
    elif not folder_path.is_dir():
        raise NotADirectoryError(str(folder_path))
    return folder_path

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-wiki',
        help = 'The wiki''s short name',
        type = str,
        required = True)
    parser.add_argument(
        '-date',
        help = 'The date the backup snapshot was taken in yyyyMMdd format',
        type = str,
        required = True)
    parser.add_argument(
        '-dest',
        help = 'The destination location to use when saving the files',
        type = writable_folder,
        required = True)
    args = parser.parse_args()    
    print(f'wiki: {args.wiki}')
    print(f'date: {args.date}')
    print(f'dest: {args.dest}')
    download_wikimedia(args.wiki, args.date, args.dest)
