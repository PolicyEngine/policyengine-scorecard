#!/usr/bin/env bash
# Propose one certified qualification's sealed results to main as a pull
# request, as #188 (6.4.1) and #190 (6.5.0) were proposed by hand. Trusted
# control code only: it reads committed public results from replay-state,
# runs main's own checks on them (verify-sealed, CI's regeneration, two
# database builds) and never installs, imports or runs candidate or release
# code; it holds no dataset token. Its pushes and pull request use the
# workflow's GitHub App token, so CI runs on the pull request as on any other.
# It never merges: that stays on the normal gates.
#
#   REQUEST_ID=<64 hex> STATE_BRANCH=replay-state \
#     bash .github/scripts/uk_replay_results_pr.sh
set -euo pipefail
: "${REQUEST_ID:?}" "${STATE_BRANCH:?}" "${RUNNER_TEMP:?}" "${GITHUB_REPOSITORY:?}"
BASE=${BASE_BRANCH:-main}
# Every third-party module the builder and the checks import (tests check).
CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema --with numpy --with pyyaml python)
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
TRAILER="Replay-Request: $REQUEST_ID"
WORK="$RUNNER_TEMP/results-pr"
STAGE="$WORK/stage"
TREE="$WORK/tree"
REQUEST="requests/$REQUEST_ID"
STATE_REF="refs/remotes/origin/$STATE_BRANCH"
BASE_REF="refs/remotes/origin/$BASE"
TAB=$(printf '\t')
# The builder is this checkout's code; the checks are the results tree's own.
HERE=$(pwd)

if ! [[ "$REQUEST_ID" =~ ^[0-9a-f]{64}$ ]]; then
  echo "::error::REQUEST_ID must be 64 lowercase hex characters" >&2
  exit 1
fi
plan() {
  python3 -I -c 'import json, sys
value = json.load(open(sys.argv[1]))
for key in sys.argv[2:]:
    value = value[key]
print("" if value is None else value)' "$WORK/plan.json" "$@"
}
builder() { PYTHONPATH="$HERE" "${CONTROL[@]}" -m pipeline.uk_replay_results_pr "$@"; }

mkdir -p "$STAGE"
git fetch -q --no-tags origin "+refs/heads/$BASE:$BASE_REF" \
  "+refs/heads/$STATE_BRANCH:$STATE_REF"
state_commit=$(git rev-parse "$STATE_REF")
if ! git cat-file -e "$state_commit:$REQUEST/STATUS.json" 2>/dev/null; then
  echo "::error::$STATE_BRANCH has no request $REQUEST_ID" >&2
  exit 1
fi
# The request directory, as data: its status, receipt, request and results.
git archive "$state_commit" "$REQUEST" | tar -x -C "$STAGE"
# The recorder guarded this output before committing it; guard it again
# before any of it is copied towards main.
python3 -I .github/scripts/uk_replay_output_guard.py "$STAGE/$REQUEST"

git worktree add -q --detach "$TREE" "$BASE_REF"
builder check --request-dir "$STAGE/$REQUEST" --checkout "$TREE" \
  --request-id "$REQUEST_ID" --state-commit "$state_commit" --plan "$WORK/plan.json"
if [ "$(plan action)" != build ]; then
  echo "::notice::No results pull request for $REQUEST_ID: $(plan reason)"
  exit 0
fi
# The receipt and results are the ones the recorder committed, unchanged since.
receipt_commit=$(plan receipt_commit)
if ! git merge-base --is-ancestor "$receipt_commit" "$state_commit" \
  || [ "$(git rev-parse "$receipt_commit:$REQUEST/REPLAY_RECEIPT.json")" \
    != "$(git rev-parse "$state_commit:$REQUEST/REPLAY_RECEIPT.json")" ] \
  || [ "$(git rev-parse "$receipt_commit:$REQUEST/results")" \
    != "$(git rev-parse "$state_commit:$REQUEST/results")" ]; then
  echo "::error::the receipt or results differ from receipt commit $receipt_commit" >&2
  exit 1
fi

# 1. The results and requirements trees, byte for byte.
git archive "$state_commit" "$REQUEST/results/results" "$REQUEST/results/docs" \
  | tar -x -C "$TREE" --strip-components=3
# 2-5. The variant record, the CI matrix, the tests and the paragraph.
builder apply --request-dir "$STAGE/$REQUEST" --checkout "$TREE" \
  --plan "$WORK/plan.json" --commit-message "$WORK/COMMIT_MESSAGE"
git -C "$TREE" add -A
git -C "$TREE" diff --cached --name-only | builder scope --plan "$WORK/plan.json"
git -C "$TREE" -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" \
  commit -q -F "$WORK/COMMIT_MESSAGE"

# Every committed result file is the blob replay-state holds.
targets=("$(plan paths namespace)" "$(plan paths requirements)")
if [ -n "$(plan paths diff)" ]; then
  targets+=("$(plan paths diff)")
fi
expected=$(git ls-tree -r "$state_commit" -- "$REQUEST/results/results" "$REQUEST/results/docs" \
  | sed "s#$TAB$REQUEST/results/#$TAB#" | LC_ALL=C sort)
committed=$(git -C "$TREE" ls-tree -r HEAD -- "${targets[@]}" | LC_ALL=C sort)
if [ "$expected" != "$committed" ]; then
  echo "::error::the committed results are not replay-state's bytes" >&2
  exit 1
fi
identical=$(printf '%s\n' "$committed" | grep -c .)

# Main's own checks, as the hand-built results PRs ran them.
(
  cd "$TREE"
  export PYTHONPATH=.
  new=$("${CONTROL[@]}" -m pipeline.uk_replay_qualify verify-sealed "$(plan paths namespace)")
  printf '%s\n' "$new"
  if [ "$(printf '%s\n' "$new" | tail -1)" != "1 sealed namespace(s) checked" ]; then
    echo "::error::the new namespace is not sealed" >&2
    exit 1
  fi
  "${CONTROL[@]}" -m pipeline.uk_replay_qualify verify-sealed | tail -1 > "$WORK/verify-sealed.txt"
  mkdir -p "$WORK/regeneration"
  RUNNER_TEMP="$WORK/regeneration" bash .github/scripts/uk_replay_regenerate.sh
  for build in 1 2; do
    uv run python -m scorecard_db.build_db "$WORK/build$build.db" > "$WORK/build$build.json"
  done
  drift=$(git status --porcelain)
  if [ -n "$drift" ]; then
    printf '%s\n' "$drift"
    echo "::error::the checks changed tracked files or left untracked ones" >&2
    exit 1
  fi
)
content_hash() { python3 -I -c 'import json, sys; print(json.load(open(sys.argv[1]))["content_hash"])' "$1"; }
if [ "$(content_hash "$WORK/build1.json")" != "$(content_hash "$WORK/build2.json")" ]; then
  echo "::error::scorecard_db.build_db is nondeterministic on the results branch" >&2
  exit 1
fi
python3 -I - "$WORK/validation.json" "$identical" "$(cat "$WORK/verify-sealed.txt")" \
  "$(content_hash "$WORK/build1.json")" <<'PY'
import json
import sys

path, identical, sealed, content_hash = sys.argv[1:]
with open(path, "w") as handle:
    json.dump(
        {
            "identical_files": int(identical),
            "verify_sealed": sealed,
            "content_hash": content_hash,
        },
        handle,
    )
PY
builder body --request-dir "$STAGE/$REQUEST" --plan "$WORK/plan.json" \
  --validation "$WORK/validation.json" --output "$WORK/BODY.md"

# Push: a new branch, or a rebuild over one that only this builder wrote.
branch=$(plan branch)
remote=$(git ls-remote --heads origin "refs/heads/$branch" | cut -f1)
head=$(git -C "$TREE" rev-parse HEAD)
pushed=false
if [ -z "$remote" ]; then
  git -C "$TREE" push -q origin "HEAD:refs/heads/$branch"
  pushed=true
else
  git fetch -q --no-tags origin "+refs/heads/$branch:refs/remotes/origin/$branch"
  if [ "$(git rev-parse "$remote^{tree}")" = "$(git -C "$TREE" rev-parse 'HEAD^{tree}')" ]; then
    echo "$branch already holds this tree"
    head=$remote
  else
    for commit in $(git rev-list "$BASE_REF..$remote"); do
      if [ "$(git log -1 --format=%ae "$commit")" != "$BOT_EMAIL" ] \
        || ! git log -1 --format=%B "$commit" | grep -qxF "$TRAILER"; then
        echo "::error::$branch holds $commit, which this builder did not write; update the branch by hand" >&2
        exit 1
      fi
    done
    git -C "$TREE" push -q --force-with-lease="refs/heads/$branch:$remote" \
      origin "HEAD:refs/heads/$branch"
    pushed=true
  fi
fi

# The pull request: opening it, or the push to its branch, starts CI on it.
# Nothing here merges it.
title=$(plan title)
number=$(gh pr list --repo "$GITHUB_REPOSITORY" --head "$branch" --base "$BASE" \
  --state open --json number --jq '.[0].number // empty')
if [ -z "$number" ]; then
  create=(--repo "$GITHUB_REPOSITORY" --base "$BASE" --head "$branch"
    --title "$title" --body-file "$WORK/BODY.md")
  if [ "$(plan draft)" = True ]; then
    create+=(--draft)
  fi
  gh pr create "${create[@]}"
elif [ "$pushed" = true ]; then
  gh pr edit "$number" --repo "$GITHUB_REPOSITORY" --title "$title" \
    --body-file "$WORK/BODY.md"
fi
echo "::notice::Results pull request for $REQUEST_ID on $branch at $head"
if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  cat "$WORK/BODY.md" >> "$GITHUB_STEP_SUMMARY"
fi
