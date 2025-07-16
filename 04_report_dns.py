import sys
from datetime import datetime
from json import loads
from time import time

from lib.util import get_org_domain, log
from lib.counters import DataPermutation
from datasets import datasets


def main(exit_early: bool = False):
    files = [datasets['de_combined2_org'], datasets['de_combined2_dmarc']]
    line_count = 0
    domain_pass = set()

    dns_error = DataPermutation(
        'DNS results domain',
        'Restricted to TXT requests',
        ['PASS', 'NXDOMAIN', 'ERROR', 'TIMEOUT'],
    )
    dns_error_timeout = DataPermutation(
        'DNS timeout error per domain',
        'Restricted to TXT requests',
        ['PASS', 'TIMEOUT'],
    )
    dns_error_nxdomain = DataPermutation(
        'DNS NXDOMAIN error per domain',
        'Check domain for org and dmrac domain',
        ['ORG', 'DMARC'],
    )

    data_collectors = [
        dns_error,
        dns_error_timeout,
        dns_error_nxdomain,
    ]

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if line:
                    line_count += 1
                    if exit_early and line_count > 100000:
                        line_count = 0
                        break

                    doc = loads(line.strip())
                    name = doc['name']
                    request_type = doc['type']
                    request = f"{request_type} {name}"
                    org_name = get_org_domain(name)
                    domain_pass.add(org_name)
                    dns_error.announce(org_name)
                    dns_error_timeout.announce(request)
                    dns_error_nxdomain.announce(org_name)

                    if 'error' in doc:
                        dns_error[org_name]['TIMEOUT'] = True
                        dns_error_timeout[request]['TIMEOUT'] = True
                    elif 'status' in doc:
                        dns_error_timeout[request]['PASS'] = True
                        status = doc['status']
                        if status == 'NXDOMAIN':
                            dns_error[org_name]['NXDOMAIN'] = True
                            if org_name == name:
                                dns_error_nxdomain[org_name]['NXDOMAIN'] = True
                            else:
                                dns_error_nxdomain[org_name]['DMARC'] = True
                        elif status != 'NOERROR':
                            dns_error[org_name]['ERROR'] = True
                        else:
                            dns_error[org_name]['PASS'] = True
                    else:
                        assert False

    valid_domain_count = len(domain_pass)

    with open('dns_report.md', mode='wt', encoding='utf-8') as fp:
        fp.write('# DNS Report \n\n')
        fp.write(f"\nApplicable domains: {valid_domain_count:,}. Line count: {line_count:,}")
        fp.write(f"\n\nReport time: {datetime.now():%Y-%m-%d %H:%M:%S%z}")

        for data_collection in data_collectors:
            fp.write('\n\n')
            data_collection.reference_sum = valid_domain_count
            data_collection.dumps(fp)


if __name__ == '__main__':
    start = time()
    log('Started execution.')
    prompt = True if sys.argv[-1] else False
    log(f"Argument: {prompt}")
    main(prompt)
    log(f"Processing time: {time() - start:.3f} s")
