import re
from time import time
from pathlib import Path
from lib.util import log

def main():
    p = re.compile('^[a-zA-Z0-9-]+\\.de$')

    domains = set()

    with open(Path('domain_lists/de_combined2.txt'), mode='rt', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            domains.add(line)
            if not p.match(line):
                log(f"Invalid domain: {line}")

    log(f"Total domains: {len(domains)}")

if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start:.3f} s")
