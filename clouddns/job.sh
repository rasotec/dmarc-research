#!/bin/bash

# --- Configuration ---
JOB_SERVER_PATH=""
API_KEY=""
SLEEP_AFTER_SUCCESS=5
RESOLVERS_FILE="/etc/clouddns/resolvers.txt"

# --- Preparation (Tag) ---
RANDOM_TAG=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 8)

# --- Set pipefail to catch errors in pipelines ---
set -o pipefail

echo "Starting processing loop..."
echo "Generated random tag: $RANDOM_TAG"

while true; do
    echo "--- New Iteration ---"

    echo "Fetching new job from job_server"
    if ! JOB_FILE_NAME=$(curl -J -O -X GET --fail -s "$JOB_SERVER_PATH/job" -H "Authorization: Bearer $API_KEY" -w "%{filename_effective}"); then
        echo "ERROR: Failed to fetch new job."
        exit 1
    fi

    if [ ! -f "$JOB_FILE_NAME" ]; then
        echo "ERROR: Job file not found."
        exit 1
    fi

    if [ "${JOB_FILE_NAME: -4}" != ".bz2" ]; then
        echo "ERROR: Job file not valid."
        exit 1
    fi

    echo "Selected job file: $JOB_FILE_NAME"
    LOCAL_UNCOMPRESSED_FILE="${JOB_FILE_NAME%.bz2}"
    echo "Decompressing $JOB_FILE_NAME to $LOCAL_UNCOMPRESSED_FILE..."
    if ! bunzip2 "$JOB_FILE_NAME"; then
        echo "ERROR: Failed to decompress $JOB_FILE_NAME."
        exit 1
    fi

    if [ ! -f "$LOCAL_UNCOMPRESSED_FILE" ]; then
        echo "ERROR: Decompressed file $LOCAL_UNCOMPRESSED_FILE not found."
        exit 1
    fi

    BASE_FILENAME=$(basename "$LOCAL_UNCOMPRESSED_FILE")
    NAME_WITHOUT_EXT="${BASE_FILENAME%.*}"
    RESULT_FILE_BASE="${NAME_WITHOUT_EXT}.ndjson"
    echo "Running massdns with input: \"$LOCAL_UNCOMPRESSED_FILE\", output file: \"$RESULT_FILE_BASE\""
    massdns --quiet --hashmap-size 2 --resolve-count 3 --retry never --interval 1000 --output Je --type NS --resolvers "$RESOLVERS_FILE" --outfile "$RESULT_FILE_BASE" "$LOCAL_UNCOMPRESSED_FILE"
    WORKER_EXIT_CODE=$?

    if [ $WORKER_EXIT_CODE -ne 0 ]; then
        echo "ERROR: massdns failed with exit code $WORKER_EXIT_CODE. Skipping upload and delete."
        exit 1
    fi
    echo "massdns invocation completed successfully."

    TAGGED_RESULT_FILE="${NAME_WITHOUT_EXT}-${RANDOM_TAG}.ndjson"
    mv "$RESULT_FILE_BASE" "$TAGGED_RESULT_FILE"
    COMPRESSED_RESULT_FILE="$TAGGED_RESULT_FILE.bz2"
    COMPRESSED_RESULT_FILE=$(basename "$COMPRESSED_RESULT_FILE")

    echo "Compressing results..."
    if ! bzip2 "$TAGGED_RESULT_FILE"; then
        echo "ERROR: Failed to compress result file $TAGGED_RESULT_FILE."
        exit 1
    fi

    DEST_URI="$JOB_SERVER_PATH/job/$COMPRESSED_RESULT_FILE"
    echo "Uploading results to $DEST_URI ..."
    if ! curl -F "file=@$COMPRESSED_RESULT_FILE" --fail-with-body -s "$DEST_URI" -H "Authorization: Bearer $API_KEY"; then
        echo "ERROR: Failed to upload $COMPRESSED_RESULT_FILE to $DEST_URI."
        exit 1
    fi
    echo "Upload complete."

    DEST_URI="$JOB_SERVER_PATH/job/$JOB_FILE_NAME"
    echo "Attempting to delete original file $DEST_URI..."
    if ! curl -X DELETE --fail-with-body -s "$DEST_URI" -H "Authorization: Bearer $API_KEY"; then
        echo "WARN: Delete command for $DEST_URI failed (Code: $?). This might be okay if file was already deleted."
    fi

    echo "Sleeping for ${SLEEP_AFTER_SUCCESS}s..."
    sleep "$SLEEP_AFTER_SUCCESS"

done # End of while true loop