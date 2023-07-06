import argparse
import os
from pathlib import Path
import shutil
from threading import Thread, Lock
import logging
from time import time
import re
from cleaner_consts import table
import unicodedata
from typing import List


"""
--source -s -> folder or path to folder --> python cleaner_1.py -s em
--output -o -> destination --> python cleaner_1.py -s folder -o sorted
"""

parser = argparse.ArgumentParser(description='App for sorting files in a folder')
parser.add_argument('-s', '--source', help='folder or path to folder for sorting inner files',
                    required=True)
parser.add_argument('-o', '--output', help='path to output folder with sorted files',
                    default='Output')
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


def process_folder(path: Path) -> None:
    created_threads: List[Thread] = []
    for el in path.iterdir():
        if el.is_file():
            thread: Thread = Thread(target=process_file, args=(el, ))
            logging.debug(f'THREAD: {thread.name} starts in {el}')
            thread.start()
            created_threads.append(thread)
        elif el.is_dir():
            thread: Thread = Thread(target=process_folder, args=(el, ))
            logging.debug(f'THREAD: {thread.name} starts in {el}')
            thread.start()
            created_threads.append(thread)
    [thr.join() for thr in created_threads if thr.is_alive()]
    [logging.debug(f'THREAD: {thr_.name} finished') for thr_ in created_threads
     if not thr_.is_alive()]


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


move_lock = Lock()


def deal_copies(file_path: Path, new_path: Path, new_name: str) -> None:
    i: int = 0
    ext: str = file_path.suffix
    root: str = '/'.join(file_path.parts[:-1])
    with move_lock:
        while True:
            file_path_renamed: Path = Path(f'{root}/{new_name}{ext}')
            os.rename(file_path, file_path_renamed)
            if file_path_renamed.name not in [file.name for file in new_path.iterdir()]:
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

# The average time of a sorting process: 0.22 sec
