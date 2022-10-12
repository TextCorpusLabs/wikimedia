import pathlib
import sys
from argparse import ArgumentParser, Namespace
from wikimedia.mode import download

def main() -> None:
    parser = ArgumentParser(prog = 'wikimedia', description = 'Tools to work with wikimedia')
    subparsers = parser.add_subparsers(help = 'sub-commands')
    download_parser(subparsers.add_parser('download', help = ' Downloads the file associated with a wikimedia data dump'))
    args = parser.parse_args()
    print_args(args)
    args.run(args)

def download_parser(parser: ArgumentParser) -> None:
    def run(args: Namespace) -> None:
        download(args.wiki, args.date, args.dest)
    parser.add_argument('-wiki', type = str, required = True, help = "The wiki''s short name")
    parser.add_argument('-date', type = str, required = True, help = 'The date the backup snapshot was taken in yyyyMMdd format')
    parser.add_argument('-dest', type = ensure_folder, required = True, help = 'The destination location to use when saving the files')
    parser.set_defaults(run = run)
    parser.set_defaults(cmd = 'download')

def ensure_folder(folder_path: str) -> pathlib.Path:
    folder= pathlib.Path(folder_path).resolve()
    if not folder.exists():
        folder.mkdir(parents = True)
    elif not folder.is_dir():
        raise NotADirectoryError(str(folder))
    return folder

def print_args(args: Namespace) -> None:
    print(f'--- {args.cmd} ---')
    for key in args.__dict__.keys():
        if key not in ['cmd', 'run']:
            print(f'{key}: {args.__dict__[key]}')
    print('---------')

if __name__ == "__main__":
    sys.exit(main())
