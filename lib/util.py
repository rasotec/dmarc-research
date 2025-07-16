import string
import random
from datetime import datetime
from dotenv import load_dotenv
from os import getenv, environ
from sys import argv
from pathlib import Path


def env_ensure(name: str) -> str:
    load_dotenv()
    value = getenv(name)
    assert value and type(value) is str, f"Environment variable {name} is not set"
    environ[name] = value
    return value


LOG_DIR = env_ensure('LOG_DIR')


def get_log_file(name: str) -> Path:
    log_dir = Path(LOG_DIR)
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
    return Path(f"{LOG_DIR}/{datetime.now():%Y%m%d_%H%M%S}-{name}.log")


def get_org_domain(domain: str) -> str:
    return '.'.join(domain.removesuffix('.').split('.')[-2:])


def get_sub_domain(domain: str) -> str:
    return '.'.join(domain.split('.')[0:-2])


def random_tag(length: int) -> str:
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def log(output: str) -> None:
    log_text = f"[{datetime.now():%Y-%m-%d %H:%M:%S%z}] {output}"
    with open(get_log_file('log'), mode='at', encoding='utf-8') as fp:
        fp.write(f"{output}\n")
    print(log_text)


log_fp = open(get_log_file('log'), mode='at', encoding='utf-8')
log_fp.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S%z}] {' '.join(argv)}")
