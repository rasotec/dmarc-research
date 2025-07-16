from time import time
from pathlib import Path
from lib.util import log
import bz2
import json

def main():
    source_dir = Path('D:/Clouddns/de_len_3')
    target_file = Path('datasets/de_len_3.ndjson')
    source_files = [child for child in source_dir.iterdir() if child.is_file() and child.suffix == '.bz2']

    with open(target_file, 'wt', encoding='utf-8') as wfp:
        for source_file in source_files:
            prefix, chunk_id, runner_tag = tuple(source_file.name.removesuffix('.ndjson.bz2').split('-'))
            with bz2.open(source_file, 'rt', encoding='utf-8') as bz2_fp:
                for line in bz2_fp:
                    if line:
                        doc = json.loads(line.strip())
                        doc['chunk_id'] = chunk_id
                        doc['runner_tag'] = runner_tag
                        wfp.write(json.dumps(doc) + '\n')


if __name__ == '__main__':
    start_time = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start_time:.3f} seconds")
