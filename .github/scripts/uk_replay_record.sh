#!/usr/bin/env bash
# Validate the uploaded outcome, commit its receipt, then commit terminal status.
set -euo pipefail
# shellcheck source=.github/scripts/uk_replay_state.sh
source .github/scripts/uk_replay_state.sh
checkout_state
"${CONTROL[@]}" - "$STATE" "$REQUEST_ID" <<'PY'
import json
import shutil
import sys
from pathlib import Path
from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_queue as queue

state, request_id = Path(sys.argv[1]), sys.argv[2]
destination = queue.request_dir(state, request_id)
try:
    outcome = json.loads(Path("output/outcome.json").read_bytes())
    source = Path("output/state/requests") / request_id
    receipt = json.loads((source / "REPLAY_RECEIPT.json").read_bytes())
    interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    if receipt["request_id"] != request_id or outcome != {
        "status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"]
    }:
        raise ValueError("the uploaded outcome does not name this request's receipt")
    results = destination / "results"
    if results.exists():
        shutil.rmtree(results)
    if (source / "results").exists():
        shutil.copytree(source / "results", results)
    shutil.copyfile(source / "REPLAY_RECEIPT.json", destination / "REPLAY_RECEIPT.json")
except Exception as error:
    receipt = queue.write_failure_receipt(
        state, request_id, code="run_artifact_failed",
        detail=f"{type(error).__name__}: {str(error).splitlines()[0]}",
    )
Path("record-outcome.json").write_text(json.dumps({
    "status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"]
}))
PY
status=$("${CONTROL[@]}" -c 'import json; print(json.load(open("record-outcome.json"))["status"])')
receipt_sha256=$("${CONTROL[@]}" -c 'import json; print(json.load(open("record-outcome.json"))["receipt_sha256"])')
push_state "Receipt for $REQUEST_ID: $status"
receipt_commit=$(git -C "$STATE" rev-parse HEAD)
"${CONTROL[@]}" -m pipeline.uk_replay_queue set-status --state "$STATE" \
  --request-id "$REQUEST_ID" --status "$status" --run-url "$RUN_URL" --now "$(now)" \
  --receipt-sha256 "$receipt_sha256" --receipt-commit "$receipt_commit"
push_state "Status for $REQUEST_ID: $status"
"${CONTROL[@]}" -m pipeline.uk_replay_queue pending --state "$STATE" --now "$(now)" > "$RUNNER_TEMP/pending.txt"
if [ -s "$RUNNER_TEMP/pending.txt" ]; then
  gh workflow run uk-replay.yml --repo "$GITHUB_REPOSITORY" --ref "$DRAIN_REF"
fi
