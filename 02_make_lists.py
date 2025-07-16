from time import time
from pathlib import Path
from lib.util import log, get_org_domain

def main():
    domains = set()

    files = [
        Path('domain_lists/de_combined.txt'),
        Path('domain_lists/de_combined2.txt'),
        Path('domain_lists/de_source2.txt'),
        Path('domain_lists/de_source3.txt'),
        Path('domain_lists/de_source1.txt'),
    ]

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                domains.add(get_org_domain(line))

    log(f"Total domains: {len(domains)}")

    with open(Path('domain_lists/de_combined3.txt'), mode='wt', encoding='utf-8') as fp:
        for domain in domains:
            fp.write(f"{domain}\n")

if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start:.3f} s")
