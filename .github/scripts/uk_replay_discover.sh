#!/usr/bin/env bash
# Read-only discovery: wheels are zip/JSON inputs, never installed or imported.
# Only `run` holds the dataset token, for the private release manifest alone.
set -euo pipefail
STATE=${STATE:-state}
DISCOVERY_DIR=${DISCOVERY_DIR:-discovery}
BASELINE="$RUNNER_TEMP/discovery-existing-skips"

case "${1:?usage: uk_replay_discover.sh snapshot|run}" in
  snapshot)
    # Public repository: no checkout credential or write permission needed.
    if git ls-remote --exit-code --heads origin "$STATE_BRANCH" >/dev/null; then
      git fetch -q origin "$STATE_BRANCH"
      git worktree add -q --detach "$STATE" FETCH_HEAD
    else
      mkdir -p "$STATE"
    fi
    mkdir -p "$BASELINE"
    shopt -s nullglob
    for path in "$STATE"/discovery/skipped/*.json; do
      [ -L "$path" ] && continue
      cp "$path" "$BASELINE/"
    done
    ;;
  run)
    # Trusted control dependencies only. No policyengine/dependency install,
    # import, subprocess probe or dataset download occurs during discovery.
    uv run --with rfc8785==0.1.4 --with jsonschema --with packaging \
      --with huggingface_hub==2.2.0 python -m pipeline.uk_replay_discover \
      --state "$STATE" --work "$RUNNER_TEMP/discovery-wheels" \
      --output-dir "$DISCOVERY_DIR/requests" --commit "$GITHUB_SHA" \
      --run-id "$GITHUB_RUN_ID"
    mkdir -p "$DISCOVERY_DIR/skipped"
    shopt -s nullglob
    for path in "$STATE"/discovery/skipped/*.json; do
      [ -L "$path" ] && continue
      if ! cmp -s "$path" "$BASELINE/${path##*/}"; then
        cp "$path" "$DISCOVERY_DIR/skipped/"
      fi
    done
    metadata=("$DISCOVERY_DIR"/requests/*.json "$DISCOVERY_DIR"/skipped/*.json)
    if [ "${#metadata[@]}" -gt 0 ]; then
      echo 'has_metadata=true' >> "$GITHUB_OUTPUT"
    else
      echo 'has_metadata=false' >> "$GITHUB_OUTPUT"
    fi
    ;;
  *)
    echo 'usage: uk_replay_discover.sh snapshot|run' >&2
    exit 2
    ;;
esac
