from time import time
from json import loads, dumps
from pathlib import Path


def main():
    with open('datasets/de_dmarc.ndjson', mode='rt', encoding='utf-8') as fp:
        for line in fp:
            doc = loads(line.strip())
            if 'data' in doc and len(doc['data']) == 3:
                print(dumps(doc, indent=4))
                return


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")
