from time import time
import json
import random

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts] for i in range(wanted_parts)]


def main():
    files = [
        'datasets/de_source2.ndjson',
        'datasets/de_source1+.ndjson',
    ]
    names = set()

    for file in files:
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                line = line.strip()
                if line:
                    doc = json.loads(line)
                    if 'data' in doc and 'type' in doc and doc['type'] == 'MX':
                        if 'answers' in doc['data']:
                            if len(doc['data']['answers']) > 0:
                                names.add(doc['name'])

    names = list(names)
    random.shuffle(names)
    chunks = split_list(names, wanted_parts=8)

    for i, chunk in enumerate(chunks):
        file = f"chunk-dmarc-{i}.txt"
        print(f"Writing chunk {file} with {len(chunk)} records")
        with open(file, mode='wt', encoding='utf-8') as fp:
            for name in chunk:
                fp.write(f"_dmarc.{name}\n")


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")

