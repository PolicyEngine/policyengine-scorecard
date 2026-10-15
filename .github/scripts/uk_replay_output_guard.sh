#!/usr/bin/env bash
# Scorecard is public: the replay's upload may hold only the receipt, status
# and sealed aggregate results. Refuse any dataset file, any file large
# enough to be one (the largest aggregate artifact is far below the limit),
# and any symlink (the upload would follow it out of the directory).
set -euo pipefail
root="${1:?usage: uk_replay_output_guard.sh <directory>}"
limit_bytes=$((25 * 1024 * 1024))
[ -d "$root" ] || exit 0
status=0
while IFS= read -r -d '' path; do
  case "$path" in
    *.h5 | *.hdf5 | *.h5.* | *.parquet | *.feather | *.pkl | *.pickle)
      echo "::error::refusing to upload a dataset-shaped file: $path"
      status=1
      ;;
  esac
  size=$(wc -c < "$path")
  if [ "$size" -gt "$limit_bytes" ]; then
    echo "::error::refusing to upload a ${size}-byte file: $path"
    status=1
  fi
done < <(find "$root" -type f -print0)
while IFS= read -r -d '' path; do
  echo "::error::refusing to upload a symlink: $path"
  status=1
done < <(find "$root" -type l -print0)
exit "$status"
