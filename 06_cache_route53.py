from time import time
from pathlib import Path
from lib.util import log
import gzip

def main():
    source_dir = Path('E:\\route53')
    target_file = Path('route53.txt')
    file_counter = 0

    with open(target_file, mode='wt', encoding='utf-8') as wfp:
        for source_file in source_dir.glob('**/*.gz'):
            file_counter += 1
            with gzip.open(source_file, 'rt', encoding='utf-8') as rfp:
                for line in rfp:
                    wfp.write(line)

    print(f"Read {file_counter} records from {source_dir}.")

if __name__ == '__main__':
    start_time = time()
    log('Started execution.')
    main()
    log(f"Processing time: {time() - start_time:.3f} seconds")
