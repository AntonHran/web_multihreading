import os
from pathlib import Path
import shutil
import time
import re
import threading
import unicodedata
import logging
from cleaner_consts import table
from concurrent.futures import ThreadPoolExecutor

output = Path('RES')


def process_file(file: str, file_path) -> None:
    _, extension = os.path.splitext(file)
    output_directory: str = os.path.join(output, extension)
    try:
        os.makedirs(output_directory, exist_ok=True)
        new_name: str = rename(file.replace(extension, ''))
        deal_with_copies(Path(file_path), output_directory, new_name)
    except OSError as error:
        logging.error(error)


def sort_with_threads(directory: str) -> None:
    with ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                executor.submit(process_file, filename, file_path, )
    executor.shutdown()


def rename(file_name: str) -> str:
    pattern = r'[a-zA-Z0-9\.\-\(\)]'
    for char in file_name:
        if not re.match(pattern, char):
            if ord(unicodedata.normalize('NFC', char.lower())) in table.keys():
                file_name = file_name.replace(char, char.translate(table))
            else:
                file_name = file_name.replace(char, '_')
    return file_name


move_lock = threading.Lock()


def deal_with_copies(old_path: Path, new_path: str, new_name: str) -> None:
    i: int = 0
    ext: str = old_path.suffix
    root: str = '/'.join(old_path.parts[:-1])
    max_attempts: int = 100
    with move_lock:
        while i < max_attempts:
            file_path_renamed: Path = Path(f'{root}/{new_name}{ext}')
            try:
                os.rename(old_path, file_path_renamed)
                shutil.move(file_path_renamed, new_path)
                break
            except (OSError, shutil.Error) as error:
                logging.error(f'{error}, {file_path_renamed}, --> '
                              f'{[file.name for file in Path(new_path).iterdir()]}')
                i += 1
                file_name: str = new_name
                new_name = f'{file_name}_{i}'
                old_path = file_path_renamed
        else:
            logging.error(f'Maximum attempts reached for {old_path}')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s - %(message)s')
    directory_: str = 'em'
    start = time.time()
    sort_with_threads(directory_)
    finish = time.time()
    print(f'You can delete the current folder now. Time: {finish - start} sec')

# The average time of a sorting process: 0,193 sec. But the program is different.
