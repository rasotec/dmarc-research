from json import loads, dumps
from time import time

from lib.util import get_org_domain, log
from datasets import datasets


def main():
    records = dict()
    file = datasets['de_combined2_dmarc']
    # file = datasets['de_combined2_org']
    with open(file, mode='rt', encoding='utf-8') as fp:
        for line in fp:
            doc = loads(line)
            name = doc['name']
            request = doc['type']
            if 'status' in doc and doc['status'] == 'NOERROR':
                if 'answers' in doc['data']:
                    answers = []
                    for answer in doc['data']['answers']:
                        answers.append({
                            'type': answer['type'],
                            'name': answer['name'],
                            'data': answer['data']
                        })
                    if not answers:
                        continue
                    item = f"{request} {name}"
                    records[item] = answers

    with open('datasets/de_combined2_dmarc_dedupe.ndjson', mode='wt', encoding='utf-8') as fp:
        for key, value in records.items():
            item = {
                'request': key,
                'answers': value
            }
            fp.write(dumps(item))
            fp.write('\n')


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
