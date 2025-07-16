from time import time
from pathlib import Path

def get_org_domain(domain: str) -> str:
    return '.'.join(domain.split('.')[-2:])

def main():
    domains = set()
    with open(Path('domain_lists/source3-domains_de.txt'), mode='rt', encoding='utf-8') as fp:
        for line in fp:
            line = line.strip().removesuffix('.')
            if line:
                org_domain = get_org_domain(line)
                domains.add(org_domain)

    print(f"Total organizational domains: {len(domains)}")
    with open(Path('domain_lists/de_source3.txt'), mode='wt', encoding='utf-8') as fp:
        for domain in domains:
            fp.write(domain + '\n')


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")