from time import time
from string import ascii_lowercase
from itertools import product

def brute(num: int):
    counter = 0
    with open(f"domain_lists/de_len_{num}.txt", mode='wt', encoding='utf-8') as fp:
        for p in product(ascii_lowercase, repeat=num):
            counter += 1
            fp.write(f"{''.join(p)}.de\n")

    print(f"Number of domains: {counter}")

if __name__ == '__main__':
    start = time()
    brute(2)
    print(f"\nProcessing time: {time() - start:.3f} s")
