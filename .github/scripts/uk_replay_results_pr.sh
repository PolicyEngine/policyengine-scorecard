#!/usr/bin/env bash
# Propose one certified qualification's sealed results to main as a pull
# request, as #188 (6.4.1) and #190 (6.5.0) were proposed by hand. Trusted
# control code only: it reads committed public results from replay-state,
# runs main's own checks on them and never installs, imports or runs
# candidate or release code; it holds no dataset token. It never merges:
# that stays on the normal gates.
#
#   uk_replay_results_pr.sh build    # job 1: the commit and every check;
#                                    # PyPI packages, no write credential
#   uk_replay_results_pr.sh rebuild  # job 2: the same commit from the same
#                                    # inputs, git and the standard library
#                                    # only; its tree must be job 1's
#   uk_replay_results_pr.sh propose  # job 2, after the App token is minted:
#                                    # push that commit and open the PR
#
# The two jobs run on separate runners, so nothing the build job's packages
# do (a $GITHUB_PATH or $GITHUB_ENV write, a planted program) reaches the job
# that holds the App token. Job 2 pushes only a commit it assembled itself,
# and only if its tree is the one job 1 verified.
set -euo pipefail
: "${REQUEST_ID:?}" "${STATE_BRANCH:?}" "${RUNNER_TEMP:?}" "${GITHUB_REPOSITORY:?}"
BASE=${BASE_BRANCH:-main}
BOT_NAME='github-actions[bot]'
BOT_EMAIL='41898282+github-actions[bot]@users.noreply.github.com'
TRAILER="Replay-Request: $REQUEST_ID"
WORK="$RUNNER_TEMP/results-pr"
STAGE="$WORK/stage"
TREE="$WORK/tree"
REQUEST="requests/$REQUEST_ID"
STATE_REF="refs/remotes/origin/$STATE_BRANCH"
BASE_REF="refs/remotes/origin/$BASE"
HERE=$(pwd)

if ! [[ "$REQUEST_ID" =~ ^[0-9a-f]{64}$ ]]; then
  echo "::error::REQUEST_ID must be 64 lowercase hex characters" >&2
  exit 1
fi
# One field of a JSON file: field FILE KEY...
field() {
  python3 -I -c 'import json, sys
value = json.load(open(sys.argv[1]))
for key in sys.argv[2:]:
    value = value[key]
print("" if value is None else value)' "$@"
}
plan() { field "$WORK/plan.json" "$@"; }
output() {
  if [ -n "${GITHUB_OUTPUT:-}" ]; then
    printf '%s=%s\n' "$1" "$2" >> "$GITHUB_OUTPUT"
  fi
}
hex() { [[ "$1" =~ ^[0-9a-f]{40}$ ]]; }

# Fetch, guard, decide, extract, edit and commit on $1 (main) from $2
# (replay-state), with builder() as the Python that runs the builder.
assemble() {
  local base_commit=$1 state_commit=$2 tab
  tab=$(printf '\t')
  mkdir -p "$STAGE"
  if ! git cat-file -e "$state_commit:$REQUEST/STATUS.json" 2>/dev/null; then
    echo "::error::$STATE_BRANCH has no request $REQUEST_ID" >&2
    exit 1
  fi
  # The request directory, as data: its status, receipt, request and results.
  git archive "$state_commit" "$REQUEST" | tar -x -C "$STAGE"
  # The recorder guarded this output before committing it; guard it again
  # before any of it is copied towards main.
  python3 -I .github/scripts/uk_replay_output_guard.py "$STAGE/$REQUEST"

  git worktree add -q --detach "$TREE" "$base_commit"
  builder check --request-dir "$STAGE/$REQUEST" --checkout "$TREE" \
    --request-id "$REQUEST_ID" --state-commit "$state_commit" --plan "$WORK/plan.json"
  if [ "$(plan action)" != build ]; then
    echo "::notice::No results pull request for $REQUEST_ID: $(plan reason)"
    output action skip
    exit 0
  fi
  # The receipt and results are the ones the recorder committed, unchanged since.
  local receipt_commit
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
  # 2-4. The variant record (CI's engine matrix reads it), the tests and the
  # paragraph. Nothing under .github/: scope refuses it.
  builder apply --request-dir "$STAGE/$REQUEST" --checkout "$TREE" \
    --plan "$WORK/plan.json" --commit-message "$WORK/COMMIT_MESSAGE"
  git -C "$TREE" add -A
  git -C "$TREE" diff --cached --name-only | builder scope --plan "$WORK/plan.json"
  git -C "$TREE" -c user.name="$BOT_NAME" -c user.email="$BOT_EMAIL" \
    commit -q -F "$WORK/COMMIT_MESSAGE"

  # Every committed result file is the blob replay-state holds.
  local targets=("$(plan paths namespace)" "$(plan paths requirements)")
  if [ -n "$(plan paths diff)" ]; then
    targets+=("$(plan paths diff)")
  fi
  local expected committed
  expected=$(git ls-tree -r "$state_commit" -- "$REQUEST/results/results" "$REQUEST/results/docs" \
    | sed "s#$tab$REQUEST/results/#$tab#" | LC_ALL=C sort)
  committed=$(git -C "$TREE" ls-tree -r HEAD -- "${targets[@]}" | LC_ALL=C sort)
  if [ "$expected" != "$committed" ]; then
    echo "::error::the committed results are not replay-state's bytes" >&2
    exit 1
  fi
  IDENTICAL=$(printf '%s\n' "$committed" | grep -c .)
}

build() {
  # Every third-party module the builder and the checks import (tests check).
  local CONTROL=(uv run --with rfc8785==0.1.4 --with jsonschema python)
  builder() { PYTHONPATH="$HERE" "${CONTROL[@]}" -m pipeline.uk_replay_results_pr "$@"; }
  git fetch -q --no-tags origin "+refs/heads/$BASE:$BASE_REF" \
    "+refs/heads/$STATE_BRANCH:$STATE_REF"
  local base_commit state_commit
  base_commit=$(git rev-parse "$BASE_REF")
  state_commit=$(git rev-parse "$STATE_REF")
  assemble "$base_commit" "$state_commit"

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
  content_hash() { field "$1" content_hash; }
  if [ "$(content_hash "$WORK/build1.json")" != "$(content_hash "$WORK/build2.json")" ]; then
    echo "::error::scorecard_db.build_db is nondeterministic on the results branch" >&2
    exit 1
  fi
  preflight
  # The verified commit, for the job that holds the token to reproduce.
  output base "$base_commit"
  output state "$state_commit"
  output tree "$(git -C "$TREE" rev-parse 'HEAD^{tree}')"
  output sealed "$(cat "$WORK/verify-sealed.txt")"
  output content_hash "$(content_hash "$WORK/build1.json")"
  output preflight "$(cat "$WORK/preflight.json")"
  output action build
  echo "verified tree $(git -C "$TREE" rev-parse 'HEAD^{tree}') for $(plan branch)"
}

# CI's format check and suite on the commit, as ci.yml's python job runs them
# (tests check the lines are its lines), then its no-drift check. A failure
# is reported, not fatal: the pull request opens as a draft that names it
# (review of 24434729, 3). This runs in the build job, which holds no write
# credential, and in a subshell without the step's command files, so nothing
# the checks run can set this job's outputs or a later step's environment.
preflight() (
  local RUFF=(uvx ruff format --check be nz scorecard_db tests pipeline)
  local SUITE=(uv run --with pytest --with hypothesis --with pypdf --with pyyaml --with numpy --with psutil --with rfc8785==0.1.4 --with jsonschema pytest tests/ -q)
  if [ -n "${GH_TOKEN:-}${GITHUB_TOKEN:-}" ]; then
    echo "::error::CI's checks run with no GitHub token in the environment" >&2
    exit 1
  fi
  unset GITHUB_ENV GITHUB_OUTPUT GITHUB_PATH GITHUB_STATE GITHUB_STEP_SUMMARY
  local ruff=0 suite=0
  (cd "$TREE" && "${RUFF[@]}") 2>&1 | tee "$WORK/ruff.log" || ruff=$?
  (cd "$TREE" && PYTHONPATH=. "${SUITE[@]}") 2>&1 | tee "$WORK/suite.log" || suite=$?
  git -C "$TREE" status --porcelain > "$WORK/porcelain.txt"
  builder preflight --ruff-exit "$ruff" --ruff-log "$WORK/ruff.log" \
    --suite-exit "$suite" --suite-log "$WORK/suite.log" \
    --porcelain "$WORK/porcelain.txt" --output "$WORK/preflight.json"
)

rebuild() {
  : "${BUILT_TREE:?}" "${BUILT_BASE:?}" "${BUILT_STATE:?}" "${BUILT_SEALED:?}" "${BUILT_CONTENT_HASH:?}" \
    "${BUILT_PREFLIGHT:?}"
  # The standard library alone: no site-packages, nothing installed. check
  # skips the schema and digest checks the build job made; the rest of the
  # builder needs no package in either job.
  builder() {
    local command=$1
    shift
    case "$command" in
      check) set -- "$@" --stdlib ;;
    esac
    python3 -I -S "$HERE/pipeline/uk_replay_results_pr.py" "$command" "$@"
  }
  if ! hex "$BUILT_TREE" || ! hex "$BUILT_BASE" || ! hex "$BUILT_STATE" \
    || ! [[ "$BUILT_SEALED" =~ ^[0-9]+\ sealed\ namespace\(s\)\ checked$ ]] \
    || ! [[ "$BUILT_CONTENT_HASH" =~ ^[0-9a-f]{16,128}$ ]]; then
    echo "::error::the build job's outputs are malformed" >&2
    exit 1
  fi
  git fetch -q --no-tags origin "+refs/heads/$BASE:$BASE_REF" \
    "+refs/heads/$STATE_BRANCH:$STATE_REF"
  # The commits the build job used must be real history of both branches,
  # and main no older than the commit this workflow runs.
  if ! git merge-base --is-ancestor "$BUILT_BASE" "$BASE_REF" \
    || ! git merge-base --is-ancestor "$BUILT_STATE" "$STATE_REF"; then
    echo "::error::the build job's base or state commit is not on $BASE or $STATE_BRANCH" >&2
    exit 1
  fi
  if [ -n "${GITHUB_SHA:-}" ] && ! git merge-base --is-ancestor "$GITHUB_SHA" "$BUILT_BASE"; then
    echo "::error::the build job's base is older than this workflow's commit $GITHUB_SHA" >&2
    exit 1
  fi
  assemble "$BUILT_BASE" "$BUILT_STATE"
  if [ "$(git -C "$TREE" rev-parse 'HEAD^{tree}')" != "$BUILT_TREE" ]; then
    echo "::error::this job's commit is not the tree the build job verified" >&2
    exit 1
  fi
  # Decide again on main as it is now: a request whose results main has
  # gained since the build job ran (a rerun after the merge) is skipped.
  # This reads the request assemble extracted and guarded, never the
  # replay-state tree directly.
  local tip
  tip=$(git rev-parse "$BASE_REF")
  if [ "$tip" != "$BUILT_BASE" ]; then
    git worktree add -q --detach "$WORK/tip" "$tip"
    builder check --request-dir "$STAGE/$REQUEST" --checkout "$WORK/tip" \
      --request-id "$REQUEST_ID" --state-commit "$BUILT_STATE" --plan "$WORK/tip-plan.json"
    if [ "$(field "$WORK/tip-plan.json" action)" != build ]; then
      echo "::notice::No results pull request for $REQUEST_ID: on main as it is now, $(field "$WORK/tip-plan.json" reason)"
      output action skip
      exit 0
    fi
  fi
  python3 -I - "$WORK/validation.json" "$IDENTICAL" "$BUILT_SEALED" "$BUILT_CONTENT_HASH" \
    "$BUILT_PREFLIGHT" <<'PY'
import json
import sys

path, identical, sealed, content_hash, preflight = sys.argv[1:]
with open(path, "w") as handle:
    json.dump(
        {
            "identical_files": int(identical),
            "verify_sealed": sealed,
            "content_hash": content_hash,
            "preflight": preflight,
        },
        handle,
    )
PY
  # body refuses a malformed preflight report, and says whether the pull
  # request is a draft: integrity is not complete, or one of CI's checks fails.
  local draft
  draft=$(python3 -I -S "$HERE/pipeline/uk_replay_results_pr.py" body --request-dir "$STAGE/$REQUEST" \
    --plan "$WORK/plan.json" --validation "$WORK/validation.json" --output "$WORK/BODY.md")
  output commit "$(git -C "$TREE" rev-parse HEAD)"
  output branch "$(plan branch)"
  output draft "$draft"
  output action build
  echo "rebuilt $(plan branch) at $(git -C "$TREE" rev-parse HEAD), tree $BUILT_TREE"
}

propose() {
  : "${BUILT_COMMIT:?}" "${BUILT_BRANCH:?}" "${BUILT_DRAFT:?}" "${GH_TOKEN:?}"
  local branch=$BUILT_BRANCH head
  # Push exactly the commit this job assembled, on the main it assembled it on.
  head=$(git -C "$TREE" rev-parse HEAD)
  if [ "$head" != "$BUILT_COMMIT" ] || [ "$branch" != "$(plan branch)" ]; then
    echo "::error::the results commit changed after it was assembled" >&2
    exit 1
  fi
  if [ "$BUILT_DRAFT" != true ] && [ "$BUILT_DRAFT" != false ]; then
    echo "::error::BUILT_DRAFT must be true or false" >&2
    exit 1
  fi
  # The token reaches git only through gh, for these commands alone.
  pushgit() { git -C "$TREE" -c credential.helper= -c 'credential.helper=!gh auth git-credential' "$@"; }

  # Push: a new branch, or a rebuild over the one commit this builder wrote.
  local remote pushed=false
  remote=$(git ls-remote --heads origin "refs/heads/$branch" | cut -f1)
  if [ -z "$remote" ]; then
    pushgit push -q origin "HEAD:refs/heads/$branch"
    pushed=true
  else
    git fetch -q --no-tags origin "+refs/heads/$branch:refs/remotes/origin/$branch"
    if [ "$(git rev-parse "$remote^{tree}")" = "$(git -C "$TREE" rev-parse 'HEAD^{tree}')" ]; then
      echo "$branch already holds this tree"
      head=$remote
    else
      # Exactly one commit, authored and committed by the bot with this
      # request's trailer: an amended or added commit is a person's work.
      local commits
      commits=$(git rev-list "$BASE_REF..$remote")
      if [ "$(printf '%s\n' "$commits" | grep -c .)" != 1 ] \
        || [ "$(git log -1 --format=%ae "$remote")" != "$BOT_EMAIL" ] \
        || [ "$(git log -1 --format=%ce "$remote")" != "$BOT_EMAIL" ] \
        || ! git log -1 --format=%B "$remote" | grep -qxF "$TRAILER"; then
        echo "::error::$branch holds work this builder did not write; update the branch by hand" >&2
        exit 1
      fi
      # The token has no workflows permission. This commit changes no
      # workflow, but the rebuilt branch also carries main's commits since
      # $remote; if one changed .github/workflows (even one main later
      # reverted), GitHub may refuse it.
      if ! pushgit push -q --force-with-lease="refs/heads/$branch:$remote" \
        origin "HEAD:refs/heads/$branch"; then
        if ! git -C "$TREE" diff --quiet "$remote" HEAD -- .github/workflows \
          || [ -n "$(git -C "$TREE" log --full-history --format=%H "$remote..HEAD" -- .github/workflows)" ]; then
          echo "::error::$branch was not updated. Main has changed .github/workflows since the branch was built, and the App token has no workflows permission. If GitHub refused the push for that, close the pull request, delete the branch and run this workflow again: a new branch holds only the bot's commit" >&2
        fi
        exit 1
      fi
      pushed=true
    fi
  fi

  # The pull request: opening it, or the push to its branch, starts CI on it.
  # Nothing here merges it.
  local title number
  title=$(plan title)
  number=$(gh pr list --repo "$GITHUB_REPOSITORY" --head "$branch" --base "$BASE" \
    --state open --json number --jq '.[0].number // empty')
  if [ -z "$number" ]; then
    local create=(--repo "$GITHUB_REPOSITORY" --base "$BASE" --head "$branch"
      --title "$title" --body-file "$WORK/BODY.md")
    if [ "$BUILT_DRAFT" = true ]; then
      create+=(--draft)
    fi
    gh pr create "${create[@]}"
  elif [ "$pushed" = true ]; then
    gh pr edit "$number" --repo "$GITHUB_REPOSITORY" --title "$title" \
      --body-file "$WORK/BODY.md"
    # A rebuild that should be a draft turns a ready pull request back into
    # one. Nothing here marks one ready: a person does, once CI passes.
    if [ "$BUILT_DRAFT" = true ]; then
      gh pr ready "$number" --repo "$GITHUB_REPOSITORY" --undo
    fi
  fi
  echo "::notice::Results pull request for $REQUEST_ID on $branch at $head"
  if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
    cat "$WORK/BODY.md" >> "$GITHUB_STEP_SUMMARY"
  fi
}

case "${1:-}" in
  build) build ;;
  rebuild) rebuild ;;
  propose) propose ;;
  *)
    echo "usage: uk_replay_results_pr.sh build|rebuild|propose" >&2
    exit 2
    ;;
esac
