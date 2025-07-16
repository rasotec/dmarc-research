import struct
from time import time
from typing import List, Iterable, Optional, Tuple
from pathlib import Path
from lib.util import log
from io import TextIOWrapper, BytesIO

LENGTH_FORMAT = 'I'
LENGTH_SIZE = struct.calcsize(LENGTH_FORMAT)
LENGTH_MAX_VALUE = 2 ** (LENGTH_SIZE * 8) - 1
PARTITION_LENGTH = 500  # Number of lines
PARTITION_FILE_EXTENSION = '.partition'


class FilePartition:
    def __init__(self, file_path: Path, descriptor: Tuple[int, int]):
        self.file_path = file_path
        self.descriptor = descriptor

    def get_io(self) -> TextIOWrapper:
        chunk_start, chunk_length = self.descriptor
        with open(self.file_path, mode='rb') as fp:
            fp.seek(chunk_start)
            chunk = fp.read(chunk_length)
        b = BytesIO(chunk)
        return TextIOWrapper(b, encoding='utf-8')

def _generate_partition_file(file_path: Path) -> None:
    assert file_path.exists(), f"Input file not found: {file_path}"
    log(f"Generating partition file for {file_path}...")
    partition_file = file_path.parent / (file_path.stem + PARTITION_FILE_EXTENSION)
    chunk_lengths: List[int] = []
    current_chunk_start_pos = 0

    with open(file_path, 'rb') as fp:
        assert fp.seekable(), "Input file must be seekable."
        while True:
            for _ in range(PARTITION_LENGTH):
                line = fp.readline()
                if not line:
                    break
            current_pos = fp.tell()
            chunk_size = current_pos - current_chunk_start_pos
            assert chunk_size >= 0, "Unexpected end of file while reading partition."
            assert chunk_size < LENGTH_MAX_VALUE, "Partition file is too large."
            current_chunk_start_pos = current_pos
            chunk_lengths.append(chunk_size)
            if not line:
                break

    with open(partition_file, 'wb') as fp:
        fp.write(struct.pack(LENGTH_FORMAT, len(chunk_lengths)))
        for length in chunk_lengths:
            fp.write(struct.pack(LENGTH_FORMAT, length))
    log(f"Partition file generated for {file_path}.")


def to_partition_descriptions(file_path: Path) -> Iterable[FilePartition]:
    assert file_path.exists(), f"Input file not found: {file_path}"
    partition_file = file_path.parent / (file_path.stem + PARTITION_FILE_EXTENSION)
    if not partition_file.exists() or file_path.stat().st_mtime > partition_file.stat().st_mtime:
        _generate_partition_file(file_path)

    assert partition_file.exists(), f"Partition file not found: {partition_file}"
    chunk_lengths: List[int] = []
    with open(partition_file, 'rb') as fpp:
        num_chunks_bytes = fpp.read(LENGTH_SIZE)
        assert len(num_chunks_bytes) == LENGTH_SIZE, "Unexpected end of file while reading chunk lengths."
        num_chunks = struct.unpack(LENGTH_FORMAT, num_chunks_bytes)[0]
        for _ in range(num_chunks):
            length_bytes = fpp.read(LENGTH_SIZE)
            assert len(length_bytes) == LENGTH_SIZE, "Unexpected end of file while reading chunk lengths."
            chunk_length = struct.unpack(LENGTH_FORMAT, length_bytes)[0]
            chunk_lengths.append(chunk_length)
        assert len(chunk_lengths) == num_chunks, "Unexpected end of file while reading chunk lengths."
        assert fpp.tell() == partition_file.stat().st_size, "Unexpected end of file while reading partition."

    current_pos = 0
    for chunk_length in chunk_lengths:
        yield FilePartition(file_path, (current_pos, chunk_length))
        current_pos += chunk_length
