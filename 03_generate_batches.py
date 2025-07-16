from time import time
from pathlib import Path
import random
import bz2
from typing import Optional, List
from lib.util import log

def split_list(alist: List[str], wanted_parts: Optional[int] = None, wanted_size: Optional[int] = None) -> List[List[str]]:
    if (wanted_parts is None and wanted_size is None) or (wanted_parts is not None and wanted_size is not None):
        raise ValueError("Exactly one of wanted_parts or wanted_size must be provided")

    length = len(alist)

    if wanted_parts is not None:
        log(f"Splitting list into {wanted_parts} parts.")
        return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]
    else:
        log(f"Splitting list into parts of size {wanted_size}.")
        return [alist[i:i + wanted_size] for i in range(0, length, wanted_size)]


def chunk_simple(domain_list_path: Path,
                 prefix: str,
                 subname: str = '',
                 output_dir: Path = Path('.'),
                 chunk_size: Optional[int] = None,
                 chunk_count: Optional[int] = None) -> None:
    if chunk_size is None and chunk_count is None:
        raise ValueError("At least one of chunk_size or chunk_count must be provided")

    log(f"Starting to process domain list: {domain_list_path}")
    domains = set()
    max_domains = None

    if chunk_size is not None and chunk_count is not None:
        max_domains = chunk_size * chunk_count
        log(f"Limiting the number of domains to a maximum of {max_domains}.")

    with open(domain_list_path, mode='rt', encoding='utf-8') as fp:
        log("Reading domains from the file...")
        for line in fp:
            domain = line.strip()
            if domain:
                domains.add(domain)
                if max_domains and len(domains) >= max_domains:
                    log(f"Reached the maximum number of domains ({max_domains}). Stopping read.")
                    break
    log(f"Finished reading. Found {len(domains)} unique domains.")

    domains = list(domains)
    log("Shuffling the list of domains...")
    random.shuffle(domains)
    log("Finished shuffling.")

    if chunk_size is not None:
        chunks = split_list(domains, wanted_size=chunk_size)
    else:
        chunks = split_list(domains, wanted_parts=chunk_count)

    log(f"Writing {len(chunks)} chunks to {output_dir}.")
    for nr, chunk in enumerate(chunks):
        output_filename = f"{prefix}-{nr + 1:05}.txt.bz2"
        output_path = output_dir / Path(output_filename)
        with bz2.open(output_path, 'wb') as dest:
            for domain in chunk:
                dest.write(f"{subname}{domain}\n".encode('utf-8'))
    log("Successfully created all domain chunks.")


def main() -> None:
    chunk_simple(domain_list_path=Path('domain_lists/de_len_4.txt'),
                 prefix='de_len_4',
                 output_dir=Path('queue'),
                 chunk_size=2500,
                 chunk_count=None)


if __name__ == '__main__':
    start_time = time()
    main()
    print(f"\nProcessing time: {time() - start_time:.3f} seconds")
