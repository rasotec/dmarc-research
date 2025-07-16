from concurrent.futures import ProcessPoolExecutor, as_completed
from json import loads
from time import time
from typing import Set

from lib.util import log
from lib.file_partition import to_partition_descriptions, FilePartition
from datasets import datasets


class WorkResult:
    def __init__(self, mx_domains: Set[str], mx_domain_records: Set[str]):
        self.mx_domains = mx_domains
        self.mx_domain_records = mx_domain_records


def do_work(file_partition: FilePartition) -> WorkResult:
    mx_domains = set()
    mx_domain_records = set()
    for line in file_partition.get_io():
        if line:
            doc = loads(line)
            name = doc['name'].rstrip('.')
            request = doc['type']
            if request != 'MX':
                continue
            if not 'status' in doc:
                continue
            status = doc['status']
            if status != 'NOERROR':
                continue
            if not 'answers' in doc['data']:
                continue
            answers = doc['data']['answers']
            for answer in answers:
                if answer['type'] == 'MX':
                    mx_domains.add(name)
                    mx_domain_records.add(answer['data'])
    result = WorkResult(mx_domains, mx_domain_records)
    return result


def main():
    file_path = datasets['de_combined2_org']
    futures_list = []
    mx_domains = set()
    mx_domain_records = set()

    with ProcessPoolExecutor() as executor:
        for file_partition in to_partition_descriptions(file_path):
            futures_list.append(executor.submit(do_work, file_partition))

        log(f"Submitted {len(futures_list)} tasks. Waiting for results...")
        for future in as_completed(futures_list):
            result = future.result()
            mx_domains.update(result.mx_domains)
            mx_domain_records.update(result.mx_domain_records)

    log(f"{len(mx_domains)=}")
    log(f"{len(mx_domain_records)=}")
    mx_domain_records = sorted(mx_domain_records)
    log(f"Writing MX domains to disk...")
    with open('results/domains_mx.txt', mode='wt', encoding='utf-8') as fp:
        for domain in mx_domains:
            fp.write(f"{domain}\n")
    log(f"Writing MX domain records to disk...")
    with open('results/domain_records_mx.txt', mode='wt', encoding='utf-8') as fp:
        for record in mx_domain_records:
            fp.write(f"{record}\n")


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
