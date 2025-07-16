# DMARC Research Scripts

This project is a collection of Python scripts designed to conduct research on DMARC records for a large list of domains. The scripts handle everything from domain list generation and validation to data collection, analysis, and reporting.

## Workflow

The project follows a sequential workflow, with scripts organized into numbered prefixes indicating the order of execution.

### 01 & 02: Domain Preparation

- **Validation & Generation:** Scripts like `01_validate_domains.py` and `02_generate_domains.py` are used to clean, validate, and prepare the initial lists of domains for the study.
- **Sampling:** `02_sample_domains.py` can be used to create smaller, more manageable datasets from larger domain lists.

### 03: DMARC Query Generation

- **Batching:** `03_generate_dmarc.py` takes the prepared domain lists and creates batches of hostnames to be queried for DMARC records (e.g., `_dmarc.example.com`).

### 04: Data Collection & Reporting

- **DNS Queries:** This stage involves querying DNS for DMARC, SPF, MX, and other record types. The project supports different DNS providers and methods (e.g., `04_report_route53.py`, `04_report_clouddns.py`).
- **Reporting:** Scripts like `04_report_dmarc.py` and `04_report_spf.py` process the raw DNS data, perform analysis, and generate reports in Markdown format.

### 05: Aggregation & Extraction

- **Data Aggregation:** `05_aggregate.py` combines data from multiple sources into a unified dataset.
- **Data Extraction:** Scripts like `05_extract_dmarc.py` are used to pull specific data points from the aggregated results for further analysis.

### 06: Caching

- **Performance:** `06_cache_clouddns.py` and `06_cache_route53.py` are used to cache DNS query results, reducing redundant queries and speeding up subsequent runs.

## Project Structure

- `domain_lists/`: Contains the initial raw lists of domains.
- `datasets/`: Contains the processed `.ndjson` datasets from the DNS queries.
- `lib/`: Contains shared library code used by the various scripts (e.g., DMARC parsing, utility functions).
- `clouddns/`: Contains scripts and configuration for running DNS queries.

## Setup and Installation

1.  **Install uv:** This project uses [uv](https://docs.astral.sh/uv/) for Python environment and project management. Follow the official instructions to install it.

2.  **Install Dependencies:**
    ```bash
    uv sync
    ```

3.  **Configure Environment:** Create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```

## Usage

The scripts are intended to be run in numerical order from the command line.

```bash
uv run python 01_validate_domains.py
uv run python 02_generate_domains.py
# ...and so on
```

Some scripts may require additional parameters.

