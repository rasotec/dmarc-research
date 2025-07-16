from time import time
from json import loads
from collections import defaultdict

from datasets import datasets
from lib.dmarc import parse_dmarc
from lib.uri import parse_uri, parse_domain
from lib.util import log, get_org_domain


def main():
    domains = defaultdict(lambda: 0)

    with open(datasets['de_combined2_dmarc'], mode='rt', encoding='utf-8') as fp:
        for line in fp:
            doc = loads(line)
            if 'data' in doc and 'type' in doc and doc['type'] == 'TXT' and 'answers' in doc['data']:
                for answer in doc['data']['answers']:
                    if 'data' in answer and answer['data'].startswith('v=DMARC1'):
                        dmarc = parse_dmarc(answer['data'])
                        if dmarc:
                            if dmarc.rua.value:
                                for value in dmarc.rua.value:
                                    uri = parse_uri(value)
                                    if not uri.error_type:
                                        if uri.email:
                                            domain = parse_domain(uri.email)
                                            if domain:
                                                domains[get_org_domain(domain)] += 1
                            if dmarc.ruf.value:
                                for value in dmarc.ruf.value:
                                    uri = parse_uri(value)
                                    if not uri.error_type:
                                        if uri.email:
                                            domain = parse_domain(uri.email)
                                            if domain:
                                                domains[get_org_domain(domain)] += 1

    domains = dict(sorted(domains.items(), key=lambda item: item[1], reverse=True))
    with open('ru_domains.txt', mode='wt', encoding='utf-8') as fp:
        for domain, count in domains.items():
            fp.write(f"{domain}: {count}\n")


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start:.3f} s")
