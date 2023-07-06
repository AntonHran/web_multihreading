import argparse
from pathlib import Path
import shutil
from threading import Thread, Lock
import logging
from time import time
import re
import unicodedata
import os
from cleaner_consts import table
from typing import List


"""
--source -s -> folder or path to folder --> python cleaner_1.py -s em
--output -o -> destination --> python cleaner_1.py -s folder -o sorted
"""

parser = argparse.ArgumentParser(description='App for sorting files in a folder')
parser.add_argument('-s', '--source', help='folder or path to folder for sorting inner files',
                    required=True)
parser.add_argument('-o', '--output', help='path to output folder with sorted files',
                    default='sorted')
args = vars(parser.parse_args())
source = args.get('source')
output = args.get('output')

folders: List[Path] = []
extensions = dict(images=('.jpeg', '.png', '.jpg', '.svg'),
                  video=('.avi', '.mp4', '.mov', '.mkv'),
                  documents=('.doc', '.docx', '.txt', '.pdf', '.xlsx', '.pptx'),
                  audio=('.mp3', '.ogg', '.wav', '.amr', '.m4a'),
                  web=('.html', '.xml', '.csv', '.json'),
                  archive=('.zip', '.rar', '.gz', '.tar'),
                  other=(), )


def get_folders(path: Path) -> None:
    for el in path.iterdir():
        if el.is_dir():
            folders.append(el)
            get_folders(el)


def get_file(file_path: Path):
    for el in file_path.iterdir():
        if el.is_file():
            handle_file(el)


def handle_file(file: Path) -> None:
    ext: str = file.suffix
    for category, extension in extensions.items():
        if ext in extension and category == 'archive':
            move_from_archive(file, category)
            break
        elif ext in extension:
            move_to(file, category)
            break
        elif ext not in extension and category == 'other':
            move_to(file, category)


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
    new_path.mkdir(exist_ok=True, parents=True)
    shutil.unpack_archive(file_path, new_path)
    os.remove(file_path)


move_lock = Lock()


def deal_copies(file_path: Path, new_path: Path, new_name: str) -> None:
    i: int = 0
    ext: str = file_path.suffix
    root: str = '/'.join(file_path.parts[:-1])
    max_attempts: int = 100
    with move_lock:
        while i < max_attempts:
            file_path_renamed: Path = Path(f'{root}/{new_name}{ext}')
            try:
                os.rename(file_path, file_path_renamed)
                shutil.move(file_path_renamed, new_path)
                break
            except (OSError, shutil.Error) as error:
                logging.error(f'{error}, {file_path_renamed}, --> '
                              f'{[file.name for file in Path(new_path).iterdir()]}')
                i += 1
                file_name: str = new_name
                new_name = f'{file_name}_{i}'
                file_path = file_path_renamed
        else:
            logging.error(f'Maximum attempts reached for {file_path}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s - %(message)s')
    base_folder = Path(source)
    output_folder = Path(output)
    folders.append(base_folder)
    start = time()
    get_folders(base_folder)

    threads: List[Thread] = []
    for folder in folders:
        thread: Thread = Thread(target=get_file, args=(folder, ))
        logging.debug(f'thread: {thread.name} starts for {folder}')
        thread.start()
        threads.append(thread)

    [th.join() for th in threads if th.is_alive()]
    [logging.debug(f'THREAD: {thr_.name} finished') for thr_ in threads if not thr_.is_alive()]
    finish = time()
    print(f'You can delete the current folder now. Time: {finish - start} sec')

# The average time of a sorting process: 0,204 sec
