#!/usr/bin/env bash
set -euo pipefail

STAGE="${1:-dev}"
REGION="${2:-us-east-1}"

log() {
  echo "[destroy-stack] $*"
}

log "Starting Serverless removal for stage '$STAGE' in region '$REGION'."

if make remove STAGE="${STAGE}" REGION="${REGION}"; then
  log "Serverless removal completed successfully for stage '$STAGE' in region '$REGION'."
else
  log "Serverless removal failed for stage '$STAGE' in region '$REGION'."
  exit 1
fi
