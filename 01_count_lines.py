from time import time
from pathlib import Path
import json
from lib.util import log
from os import getenv, environ
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = getenv('CACHE_DIR')
environ['CACHE_DIR'] = CACHE_DIR

CACHE_FILE = Path(CACHE_DIR) / 'line_count_cache.json'

def load_cache():
    """Load the line count cache from a JSON file."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'rt', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save the line count cache to a JSON file."""
    with open(CACHE_FILE, 'wt', encoding='utf-8') as f:
        json.dump(cache, f, indent=2)

def main():
    target_directory = Path('domain_lists')
    cache = load_cache()

    for filename in target_directory.iterdir():
        if filename.name.endswith('.txt'):
            file_path = str(filename)
            mtime = filename.stat().st_mtime

            # Check if we have a valid cached result
            if (file_path in cache and
                'mtime' in cache[file_path] and
                'line_count' in cache[file_path] and
                cache[file_path]['mtime'] == mtime):
                # Use cached result
                num_lines = cache[file_path]['line_count']
                log(f"{filename.name}: {num_lines:,} (cached)")
            else:
                # Count lines and update cache
                with open(filename, 'rt', encoding='utf-8') as f:
                    num_lines = len(f.readlines())

                # Update cache
                cache[file_path] = {
                    'mtime': mtime,
                    'line_count': num_lines
                }
                log(f"{filename.name}: {num_lines:,}")

    # Save the updated cache
    save_cache(cache)

if __name__ == '__main__':
    start = time()
    log("Script started.")
    main()
    log(f"Processing time: {time() - start:.3f} s")
