#!/bin/bash

# --- Configuration ---
S3_SCRIPT_URI="s3://.../job.sh"
S3_LOGS_URI="s3://.../logs/"
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/clouddns.XXXXXXXXXX")
LOCAL_SCRIPT_PATH="$TMP_DIR/job.sh"
LOG_FILE="$(hostname)-$(date '+%Y%m%d-%H%M%S').log"

# --- Script Logic ---
echo "Change to working directory: $TMP_DIR"
cd "$TMP_DIR" || {
    echo "Error: Could not navigate to $TMP_DIR."
    exit 1
}

echo "Current Working Directory: $(pwd)"
echo "Current user: $(whoami)"
echo "Attempting to download script from $S3_SCRIPT_URI to $LOCAL_SCRIPT_PATH"

aws s3 cp --quiet --no-progress "$S3_SCRIPT_URI" "$LOCAL_SCRIPT_PATH" || {
    echo "Error: Failed to download script from S3 URI: $S3_SCRIPT_URI. Exiting."
    exit 1
}
echo "Download successful."

echo "Execute permission set for ${LOCAL_SCRIPT_PATH}."
chmod +x "$LOCAL_SCRIPT_PATH" || {
    echo "Error: Setting permissions failed"
    exit 1
}

echo "Start job script"
"$LOCAL_SCRIPT_PATH"
echo "Job script stopped"

echo "Creating log file"
journalctl --unit clouddns.service --boot -0 > "$LOG_FILE"

echo "Compressing log file"
bzip2 "$LOG_FILE" || echo "Error: Compression of log file failed"

echo "Uploading log file"
aws s3 cp --quiet --no-progress "$LOG_FILE.bz2" "$S3_LOGS_URI" || echo "Error: Upload of log file failed"

echo "Sleeping for 60 seconds"
sleep 60
echo "Initiating system shutdown..."
shutdown +1
echo "Main script finished."