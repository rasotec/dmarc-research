from pathlib import Path
from json import loads
from time import time
from lib.dmarc import parse_dmarc, dmarc_heuristic


def main() -> None:
    """
    Extract invalid DMARC records from a DMARC file.
    Condition: dmarc exists in
    :return:
    """
    dataset_file = Path('datasets') / 'de_dmarc.ndjson'
    result_file = Path('results') / 'invalid_dmarc_records.txt'
    invalid_dmarc_records = set()
    line_count = 0

    with open(dataset_file, mode='rt', encoding='utf-8') as fp:
        for line in fp:
            line_count += 1
            if line_count % 100000 == 0:
                print(f"Processed {line_count} lines")

            doc = loads(line.strip())
            if 'data' in doc and 'type' in doc and doc['type'] == 'TXT':
                doc_data = doc['data']
                if 'answers' in doc_data:
                    for answer in doc_data['answers']:
                        if 'data' in answer:
                            data = answer['data']
                            # TODO: check answer type, it could be != TXT
                            if dmarc_heuristic(data):
                                dmarc_request = parse_dmarc(data)
                                if not dmarc_request:
                                    invalid_dmarc_records.add(data)

    print(f"\nFound {len(invalid_dmarc_records):,} invalid DMARC records")

    with open(result_file, 'wt', encoding='utf-8') as fp:
        for record in invalid_dmarc_records:
            fp.write(f"{record}\n")


if __name__ == '__main__':
    start = time()
    main()
    print(f"\nProcessing time: {time() - start:.3f} s")
