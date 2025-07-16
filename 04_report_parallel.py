from concurrent.futures import ProcessPoolExecutor, as_completed
from json import loads
from pathlib import Path
from time import time
from io import TextIOWrapper, BytesIO
from typing import Tuple

from lib.util import log
from lib.file_partition import to_partition_descriptions
from datasets import datasets


def do_work(file_path: Path, descriptor: Tuple[int, int]) -> int:
    chunk_start, chunk_length = descriptor
    with open(file_path, mode='rb') as fp:
        fp.seek(chunk_start)
        chunk = fp.read(chunk_length)
    b = BytesIO(chunk)
    w = TextIOWrapper(b, encoding='utf-8')
    count = 0
    for line in w:
        if line:
            doc = loads(line.strip())
            name = doc['name']
            count += len(name)
    return count


def main():
    count = 0
    file_path = datasets['de_combined2_org']
    futures_list = []

    with ProcessPoolExecutor() as executor:
        for descriptor in to_partition_descriptions(file_path):
            future = executor.submit(do_work, file_path, descriptor)
            futures_list.append(future)

        log(f"\nSubmitted {len(futures_list)} tasks. Waiting for results...")
        for future in as_completed(futures_list):
            count += future.result()

    log(f"{count=}")


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
