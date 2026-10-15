#!/usr/bin/env bash
# Candidate code runs only here, in the read-only job without the dataset token.
set -euo pipefail
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema --with huggingface_hub python)
mkdir -p output/state

if "${CONTROL[@]}" -m pipeline.uk_replay_qualify run-request \
  --request input/REQUEST.json --state-dir output/state \
  --work "$RUNNER_TEMP/requests/$REQUEST_ID" --runner "$REPLAY_RUNNER" \
  --dataset-file input/dataset.h5 --dataset-result input/fetch-result.json \
  --result-file output/outcome.json; then
  run_exit=0
else
  run_exit=$?
  echo "::error::run-request exited $run_exit; the recorder will preserve its receipt or write a failed receipt"
fi
printf '%s\n' "$run_exit" > output/run-exit.txt
# Do not hide pipeline stdout, and always allow the result artifact to upload.
