from time import time
import json
from pathlib import Path

def main():
    dataset = dict()

    for file in Path('datasets').glob('*.ndjson'):
        with open(file, mode='rt', encoding='utf-8') as fp:
            for line in fp:
                doc = json.loads(line.strip())
                if 'name' in doc:
                    if doc['name'] not in dataset:
                        dataset[doc['name']] = [doc]
                    else:
                        dataset[doc['name']].append(doc)

    print(f"Loaded {len(dataset)} domains")


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")

