from time import time
from lib.util import log

def load_suffixes(filename):
    with open(filename, mode='rt', encoding='utf-8') as fp:
        return [f".{line.strip()}" for line in fp]


def main():
    log('Loading suffixes')
    suffixes = load_suffixes('public_suffix_list_de.dat')

    log('Processing domains')
    with open('domain_lists/de_source3.txt', mode='rt', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip()
            # Check if domain ends with any of the suffixes
            if any(line.endswith(suffix) for suffix in suffixes):
                log(line)


if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start:.3f} s")
