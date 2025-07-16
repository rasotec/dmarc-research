import re
import sys
from time import time
from pathlib import Path
from collections import defaultdict, namedtuple
from typing import Optional

from lib.util import get_org_domain, get_sub_domain, log
from statistics import median
from datetime import datetime

Route53Record = namedtuple('Route53Record', [
    'date', 'version', 'distribution_id', 'request_name', 'request_type',
    'response_code', 'protocol', 'edge_location', 'ip_address', 'ip_net'
])


def parse(line: str) -> Optional[Route53Record]:
    parts = line.strip().split(' ')
    if len(parts) != 11:
        return None
    return Route53Record(
        date=datetime.strptime(parts[0], '%Y-%m-%dT%H:%M:%S.%fZ'),
        version=parts[1],
        distribution_id=parts[3],
        request_name=parts[4],
        request_type=parts[5],
        response_code=parts[6],
        protocol=parts[7],
        edge_location=parts[8],
        ip_address=parts[9],
        ip_net=parts[10],
    )


def m1():
    route53_file = Path('route53.txt')
    zones = defaultdict(lambda: 0)
    with open(route53_file, 'rt', encoding='utf-8') as rfp:
        for line in rfp:
            line = line.strip()
            if line:
                parts = line.split(' ')
                if len(parts) == 11:
                    zones[parts[3]] += 1

    for zone, count in zones.items():
        print(f"{zone}: {count}")


def m2():
    route53_file = Path('route53.txt')
    dmarcs = defaultdict(lambda: 0)
    for line in route53_file.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if line:
            parts = line.split(' ')
            if len(parts) == 11:
                sub = get_sub_domain(parts[4])
                if sub == '_dmarc':
                    dmarcs[parts[3]] += 1

    for zone, count in dmarcs.items():
        log(f"{zone}: {count}")

    log(f"{median(dmarcs.values())}")


def m3(records: list[Route53Record]) -> None:
    days = defaultdict(lambda: {'requests': 0, 'zones': set()})
    p = re.compile('^_dmarc.[a-zA-Z0-9-]+\\.[a-z]+$')
    for record in records:
        if record.request_type != 'TXT':
            continue
        if p.match(record.request_name) is None:
            continue
        if record.response_code != 'NOERROR':
            continue
        days[record.date.date()]['requests'] += 1
        days[record.date.date()]['zones'].add(record.distribution_id)

    for day, data in days.items():
        log(f"{day}: {data['requests']:,} requests, {len(data['zones']):,} zones, {data['requests'] / len(data['zones']):.1f} requests / zone")

    sorted_data = dict(sorted(days.items(), key=lambda item: item[0]))

    days_str = [f"'{day}T12:00:00Z'" for day in sorted_data.keys()]
    print(f"[{', '.join(days_str)}]")

    values = [f"{data['requests'] / len(data['zones']):.0f}" for data in sorted_data.values()]
    print(f"[{', '.join(values)}]")


def m4(records: list[Route53Record]) -> None:
    days = defaultdict(lambda: defaultdict(lambda: 0))
    p = re.compile('^_dmarc.[a-zA-Z0-9-]+\\.[a-z]+$')
    for record in records:
        if record.request_type != 'TXT':
            continue
        if p.match(record.request_name) is None:
            continue
        if record.response_code != 'NOERROR':
            continue
        days[record.date.date()][record.distribution_id] += 1

    days = dict(sorted(days.items(), key=lambda item: item[0]))
    for day, data in days.items():
        log(f"{day}: {', '.join([str(v) for v in data.values()])}")

def m5(records: list[Route53Record]) -> None:
    ips = defaultdict(lambda: 0)
    p = re.compile('^_dmarc.[a-zA-Z0-9-]+\\.[a-z]+$')
    for record in records:
        if record.response_code != 'NOERROR':
            continue
        if record.request_type != 'TXT':
            continue
        if p.match(record.request_name) is None:
            continue
        ips[record.ip_address] += 1

    ips = dict(sorted(ips.items(), key=lambda item: item[1]))
    for ip, count in ips.items():
        log(f"{ip}: {count}")

def main():
    user_method = sys.argv[-1]
    log(f"Argument: {user_method}")
    record_count = 0
    records = []
    for line in Path('route53.txt').read_text(encoding='utf-8').splitlines():
        record = parse(line)
        if record:
            record_count += 1
            records.append(record)
    log(f"Total records: {record_count:,}")
    globals()[user_method](records)


if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start:.3f} s")
