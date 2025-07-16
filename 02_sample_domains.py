from time import time
from random import sample


def main():
    domains = set()
    with open('domain_lists/de_combined.txt', mode='rt', encoding='utf-8') as fp:
        for line in fp:
            domains.add(line.strip())

    domains = sample(list(domains), 50000)

    with open('server_tests/sample_domains_small.txt', mode='wt', encoding='utf-8') as fp:
        for domain in domains:
            fp.write(f"{domain}\n")


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")
