import argparse
from pathlib import Path
import shutil
import logging
from time import time
import concurrent.futures
import re
import unicodedata
from cleaner_consts import table
import os


"""
--source -s -> folder or path to folder --> python cleaner_1.py -s em
--output -o -> destination --> python cleaner_1.py -s folder -o sorted
"""

parser = argparse.ArgumentParser(description='App for sorting files in a folder')
parser.add_argument('-s', '--source', help='folder or path to folder for sorting inner files',
                    required=True)
parser.add_argument('-o', '--output', help='path to output folder with sorted files',
                    default='result')
args = vars(parser.parse_args())
source = args.get('source')
output = args.get('output')

extensions = dict(images=('.jpeg', '.png', '.jpg', '.svg'),
                  video=('.avi', '.mp4', '.mov', '.mkv'),
                  documents=('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
                  audio=('.mp3', '.ogg', '.wav', '.amr', '.m4a'),
                  web=('.html', '.xml', '.csv', '.json'),
                  archive=('.zip', '.rar', '.gz', '.tar'),
                  other=(), )


def sort_through_threads(file_path: Path, workers_number: int) -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_number, ) as executor:
        logging.debug(f'THREAD_POOL_EXECUTOR starts in {file_path}')
        executor.submit(process_folder, file_path)


def process_folder(path: Path) -> None:
    for el in path.iterdir():
        if el.is_file():
            process_file(el)
        elif el.is_dir():
            if len(list(el.iterdir())) >= 5:
                sort_through_threads(el, len(list(el.iterdir())))
            else:
                process_folder(el)


def process_file(file_path: Path) -> None:
    ext: str = file_path.suffix
    for category, extension in extensions.items():
        if ext in extension and category == 'archive':
            move_from_archive(file_path, category)
            break
        elif ext in extension:
            move_to(file_path, category)
            break
        elif ext not in extension and category == 'other':
            move_to(file_path, category)


def check_name(file_name: str) -> str:
    pattern = r'[a-zA-Z0-9\.\-\(\)]'
    for char in file_name:
        if not re.match(pattern, char):
            if ord(unicodedata.normalize('NFC', char.lower())) in table.keys():
                file_name = file_name.replace(char, char.translate(table))
            else:
                file_name = file_name.replace(char, '_')
    return file_name


def move_to(file_path: Path, category: str) -> None:
    new_name: str = check_name(file_path.name.replace(file_path.suffix, ''))
    new_path: Path = output_folder/category.title()
    try:
        new_path.mkdir(exist_ok=True, parents=True)
        deal_copies(file_path, new_path, new_name)
    except OSError as error:
        logging.error(error)


def move_from_archive(file_path: Path, category: str) -> None:
    new_name: str = check_name(file_path.name.replace(file_path.suffix, ''))
    new_path: Path = output_folder / category.title() / new_name
    try:
        new_path.mkdir(exist_ok=True, parents=True)
        shutil.unpack_archive(file_path, new_path)
        os.remove(file_path)
    except OSError as error:
        logging.error(error)


def deal_copies(file_path: Path, new_path: Path, new_name: str) -> None:
    i: int = 0
    ext: str = file_path.suffix
    root: str = '/'.join(file_path.parts[:-1])
    while True:
        file_path_renamed: Path = Path(f'{root}/{new_name}{ext}')
        os.rename(file_path, file_path_renamed)
        if not Path(new_path/f'{new_name}{ext}').exists():
            shutil.move(file_path_renamed, new_path)
            break
        i += 1
        file_name: str = new_name
        new_name = f'{file_name}_{i}'
        file_path = file_path_renamed


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s - %(message)s')
    base_folder: Path = Path(source)
    start: time = time()
    output_folder: Path = Path(output)
    process_folder(base_folder)
    finish: time = time()
    print(f'You can delete the current folder now. Time: {finish - start} sec')

# The average time of a sorting process: 0.207 sec
