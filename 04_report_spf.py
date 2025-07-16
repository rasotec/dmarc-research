from datetime import datetime
from json import loads
from time import time

from lib.util import get_org_domain, log
from lib.counters import DataCounter
from datasets import datasets


def main():
    files = [datasets['de_combined2_org']]
    line_count = 0
    exit_early = False

    domain_pass = set()

    spf_all_mechanism = DataCounter(
        'SPF all mechanism',
        'Shows how many different SPF mechanisms were found in the responses. The sum percentage is relative to all successful domain queries.',
        'Mechanism'
    )

    data_collectors = [
        spf_all_mechanism
    ]

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line_count += 1
                if exit_early and line_count > 10000:
                    line_count = 0
                    break

                doc = loads(line.strip())
                name = doc['name']
                org_name = get_org_domain(name)
                is_org_domain = org_name == get_org_domain(name)
                is_ok = 'error' not in doc and 'status' in doc and doc['status'] == 'NOERROR'

                if is_ok and doc['type'] == 'TXT' and is_org_domain:
                    if 'data' in doc and 'answers' in doc['data']:
                        domain_pass.add(org_name)
                        for answer in doc['data']['answers']:
                            answer_data: str = answer['data']
                            if answer_data.startswith('v=spf1'):
                                spf_fragments = answer['data'].split(' ')
                                all_mechanism = spf_fragments[-1]
                                if all_mechanism in ['-all', '~all', '?all', '+all']:
                                    spf_all_mechanism[spf_fragments[-1]] += 1
                                else:
                                    spf_all_mechanism['other'] += 1

    valid_domain_count = len(domain_pass)

    with open('spf_report.md', mode='wt', encoding='utf-8') as fp:
        fp.write('# SPF Report \n\n')
        fp.write(f"\nApplicable domains: {valid_domain_count:,}")
        fp.write(f"\nReport time: {datetime.now():%Y-%m-%d %H:%M:%S%z}")

        for data_collection in data_collectors:
            fp.write('\n\n')
            data_collection.reference_sum = valid_domain_count
            data_str = data_collection.dump()
            fp.write(data_str)


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
