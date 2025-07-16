from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from json import loads
from time import time
from typing import Dict

from lib.counters import DataCounter, merge_dicts
from lib.dmarc import parse_dmarc
from lib.util import log
from lib.file_partition import to_partition_descriptions, FilePartition
from datasets import datasets

def make_counters() -> dict:
    return {
        'meta': defaultdict(int),
        'policy': defaultdict(int),
        'errors': defaultdict(int),
        'config': defaultdict(int),
    }

def do_work(file_partition: FilePartition) -> Dict[str, Dict]:
    counters = make_counters()

    for line in file_partition.get_io():
        if line:
            doc = loads(line)
            request = doc['request']
            assert type(request) is str
            answers = doc['answers']
            assert type(answers) is list
            name = request.split()[1]
            counters['meta']['line_counter'] += 1

            dmarc_answers = []
            dmarc_found = False
            for answer in answers:
                if type(answer) is not dict:
                    print(answer)
                assert type(answer) is dict
                if answer['type'] == 'TXT':
                    txt_answer = answer['data']
                    if txt_answer.startswith('v'): # rfc7489 text says 'v=', but spec (and parser) allows whitespace in between
                        dmarc_answers.append(txt_answer)
                        if not dmarc_found:
                            dmarc_found = True

            if len(dmarc_answers) > 1:
                counters['errors']['multiple TXT answers'] += 1
                continue
            elif len(dmarc_answers) == 0:
                counters['errors']['no TXT answers'] += 1
                continue

            dmarc_request = parse_dmarc(dmarc_answers[0])
            if not dmarc_request:
                counters['errors']['syntax of record invalid'] += 1
                continue

            counters['errors']['pass'] += 1
            counters['policy'][dmarc_request.p.value.value] += 1
    return counters


def main():
    file_path = datasets['de_combined2_dmarc_dedupe']
    futures_list = []

    counters_all = {
        'meta': DataCounter('Total domains', 'just to count all domains', '#'),
        'policy': DataCounter('DMARC Policy', 'DMARC policy', 'p='),
        'errors': DataCounter('DMARC Errors', 'DMARC errors', '#'),
        'config': DataCounter('DMARC config', 'DMARC configuration', '#'),
    }

    counters = make_counters()

    with ProcessPoolExecutor() as executor:
        for file_partition in to_partition_descriptions(file_path):
            futures_list.append(executor.submit(do_work, file_partition))

        log(f"Submitted {len(futures_list)} tasks. Waiting for results...")
        for future in as_completed(futures_list):
            result = future.result()
            for counter_name, counter in counters.items():
                counters[counter_name] = merge_dicts(result[counter_name], counter)

    reference_sum = counters['meta']['line_counter']
    for counter_name, counter in counters_all.items():
        counters_all[counter_name].update(counters[counter_name])

    log(f"Writing report to disk...")
    with open('dmarc_report_fast.md', mode='wt', encoding='utf-8') as fp:
        fp.write('# DMARC Report \n\n')
        for counter in counters_all.values():
            counter.reference_sum = reference_sum
            counter.dumps(fp)
            fp.write('\n\n')


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
