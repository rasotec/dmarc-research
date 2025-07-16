from collections import defaultdict
from datetime import datetime
from json import loads
from time import time

from lib.util import log
from datasets import datasets


def main():
    files = [datasets['de_combined2_org'], datasets['de_combined2_dmarc']]
    line_count = 0
    exit_early = False

    requests = defaultdict(lambda: 0)

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line_count += 1
                if exit_early and line_count > 100000:
                    line_count = 0
                    break

                doc = loads(line.strip())
                name = doc['name']
                request = doc['type']
                item = f"{request} {name}"
                requests[item] += 1

    distribution = defaultdict(lambda: 0)
    for value in requests.values():
        distribution[value] += 1

    distribution = dict(sorted(distribution.items(), key=lambda item: item[1], reverse=True))

    with open('duplicates_report.md', mode='wt', encoding='utf-8') as fp:
        fp.write('# Duplicates Report \n\n')
        fp.write(f"\nLine count: {line_count:,}")
        fp.write(f"\nReport time: {datetime.now():%Y-%m-%d %H:%M:%S%z}\n")

        for k, v in distribution.items():
            fp.write(f"\n{k}: {v:,}")


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
