from datetime import datetime
from json import loads
from time import time

from lib.util import log
from datasets import datasets


def main():
    files = [datasets['de_combined2_org'], datasets['de_combined2_dmarc']]
    line_count = 0
    exit_early = False

    for file in files:
        min_rx_ts = None
        max_rx_ts = None
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line_count += 1
                if exit_early and line_count > 100000:
                    line_count = 0
                    break

                doc = loads(line.strip())
                if 'rx_ts' in doc:
                    rx_ts = doc['rx_ts']
                    if min_rx_ts is None or rx_ts < min_rx_ts:
                        min_rx_ts = rx_ts
                    if max_rx_ts is None or rx_ts > max_rx_ts:
                        max_rx_ts = rx_ts

        start_time = datetime.fromtimestamp(min_rx_ts / 1000000000.0)
        end_time = datetime.fromtimestamp(max_rx_ts / 1000000000.0)
        diff = end_time - start_time
        log(f"File: {file}")
        log(f"Start time: {start_time:%Y-%m-%d %H:%M:%S%z}")
        log(f"End time: {end_time:%Y-%m-%d %H:%M:%S%z}")
        log(f"Time difference: {diff}")


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
