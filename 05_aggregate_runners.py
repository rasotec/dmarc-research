from collections import defaultdict
from time import time
import json
from datasets import datasets
from lib.util import log

def main():
    runners = defaultdict(lambda: 0)

    for file in [datasets['de_combined2_dmarc'], datasets['de_combined2_org']]:
        log(f"Processing {file}")
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                doc = json.loads(line.strip())
                runners[doc['runner_tag']] += 1

    log(f"Loaded data about {len(runners)} runners")
    sorted_runners = dict(sorted(runners.items(), key=lambda item: item[1], reverse=True))

    for runner, count in sorted_runners.items():
        log(f"{runner}: {count:,}")


if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"\nProcessing time: {time() - start:.3f} s")

