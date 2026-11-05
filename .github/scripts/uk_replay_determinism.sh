#!/usr/bin/env bash
# The certified variant's code runs only here: as the unprivileged candidate
# account, in its private copy of the repository (uk_replay_sandbox.sh install,
# then replay), after the dataset was fetched. Nothing here holds a token.
# `install` has the network and no dataset; `replay` has the dataset and no
# network. Only output/ goes back to the runner, whose own Python compares it
# with the committed artifact (pipeline/uk_replay_determinism.py).
set -euo pipefail
VENV=.venv-variant

case "${1:?usage: uk_replay_determinism.sh install|replay}" in
  install)
    uv venv --python 3.12 "$VENV"
    uv pip install --python "$VENV/bin/python" -r "${REQUIREMENTS:?}"
    uv pip install --python "$VENV/bin/python" rfc8785==0.1.4 jsonschema
    ;;
  replay)
    # compute_uk_event's preflight checks the installed environment is
    # exactly the variant's, and the dataset's SHA-256, before it simulates.
    work=.venv-replay-checks/determinism
    rm -rf output "$work"
    mkdir output
    "$VENV/bin/python" -m pipeline.compute_uk_event --event "${REPLAY_EVENT:?}" \
      --variant "${VARIANT:?}" --measures "${REPLAY_MEASURE:?}" --years "${REPLAY_YEAR:?}" \
      --workers 1 --dataset-file input/dataset.h5 --output-dir "$work"
    cp "$work/${REPLAY_MEASURE}_${REPLAY_YEAR}.json" output/
    ;;
  *)
    echo "usage: uk_replay_determinism.sh install|replay" >&2
    exit 2
    ;;
esac
