"""The results pull request: its permission boundary, its edits checked
against the hand-built 6.4.1 and 6.5.0 results PRs, and the whole builder
run against a local bare remote with a stub GitHub CLI.

Invariants (each has deterministic cases and, where it ranges over inputs, a
Hypothesis property):

* the index only grows: the new document is the old one plus one record, in
  canonical form;
* after the edit the engine matrix lists exactly the certified variants, and
  nothing else in ci.yml changes;
* the paragraph states every nonzero flag count and no zero one;
* a commit touches the extracted results and the five edits, nothing else;
* every committed result file has the blob replay-state holds;
* the same request on the same main pushes nothing the second time.
"""

import ast
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from hypothesis import given, settings
from hypothesis import strategies as st

from pipeline import uk_replay_interface as interface
from pipeline import uk_replay_qualify as qualify
from pipeline import uk_replay_results_pr as builder
from pipeline import uk_replay_variants as rv
from pipeline.compute_uk_event import canonical_bytes

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github/workflows/uk-replay-results.yml"
SCRIPT = ROOT / ".github/scripts/uk_replay_results_pr.sh"
RECORD = ROOT / ".github/scripts/uk_replay_record.sh"
RUN = "https://github.com/PolicyEngine/policyengine-scorecard/actions/runs/7"
REPOSITORY = "PolicyEngine/policyengine-scorecard"
PE641 = "pe6.4.1_uk2.130.1_policyengine-uk-data-1.58.1"
PE650 = "pe6.5.0_uk2.130.1_policyengine-uk-data-1.58.1"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"


def git(directory, *arguments, check=True):
    return subprocess.run(
        ["git", "-C", str(directory), *arguments],
        check=check,
        capture_output=True,
        text=True,
    ).stdout.strip()


def committed_record(variant_id):
    return copy.deepcopy(rv.get_variant(variant_id))


def committed_receipt(variant_id):
    return json.loads(
        (ROOT / rv.REPLAY_RESULT_ROOT / variant_id / rv.RECEIPT_NAME).read_bytes()
    )


def flat(text):
    return " ".join(text.split())


# --- the permission boundary ---------------------------------------------------


def test_the_results_workflow_is_dispatch_only_main_only_and_holds_no_dataset_token():
    text = WORKFLOW.read_text()
    document = yaml.safe_load(text)
    # PyYAML reads the bare key `on` as True. Never pull_request (or its
    # target variant), push or schedule.
    assert set(document[True]) == {"workflow_dispatch"}
    assert set(document[True]["workflow_dispatch"]["inputs"]) == {"request_id"}
    assert document["permissions"] == {"contents": "read"}
    assert document["concurrency"] == {
        "group": "uk-replay-results-${{ github.event.inputs.request_id }}",
        "cancel-in-progress": False,
    }
    assert "PE_UK_PRIVATE_HF_READ_TOKEN" not in text
    assert "HUGGING_FACE_TOKEN" not in text
    (name,) = document["jobs"]
    job = document["jobs"][name]
    # GITHUB_TOKEN reads; only the App token writes.
    assert job["permissions"] == {"contents": "read"}
    assert job["if"] == (
        "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"
    )
    token, checkout, setup, run = job["steps"]
    # The App's key reaches only the step that mints a token scoped to this
    # repository: contents and pull requests to push and open the PR, and
    # workflows because the commit edits ci.yml's matrix.
    assert token["uses"] == "actions/create-github-app-token@v2"
    assert token["id"] == "token"
    assert token["with"] == {
        "app-id": "${{ secrets.APP_ID }}",
        "private-key": "${{ secrets.APP_PRIVATE_KEY }}",
        "permission-contents": "write",
        "permission-pull-requests": "write",
        "permission-workflows": "write",
    }
    assert "owner" not in token["with"] and "repositories" not in token["with"]
    holders = [step for step in job["steps"] if "secrets." in json.dumps(step)]
    assert holders == [token]
    assert "secrets." not in json.dumps({k: v for k, v in job.items() if k != "steps"})
    assert checkout["uses"] == "actions/checkout@v4"
    assert checkout["with"] == {
        "fetch-depth": 0,
        "token": "${{ steps.token.outputs.token }}",
    }
    assert setup["uses"] == "astral-sh/setup-uv@v5"
    assert setup["with"] == {"enable-cache": False}
    assert run["run"] == "bash .github/scripts/uk_replay_results_pr.sh"
    assert run["env"] == {
        "REQUEST_ID": "${{ github.event.inputs.request_id }}",
        "STATE_BRANCH": "replay-state",
        "BASE_BRANCH": "${{ github.event.repository.default_branch }}",
        "GH_TOKEN": "${{ steps.token.outputs.token }}",
    }
    for step in job["steps"]:
        assert "${{" not in step.get("run", "")
        assert not step.get("uses", "").startswith(("actions/cache", "actions/upload"))


def test_the_builder_runs_no_release_code_and_never_merges():
    script = SCRIPT.read_text()
    for forbidden in (
        "uv venv",
        "pip install",
        "uk_replay_sandbox.sh",
        "uk_replay_drain.sh",
        "run-request",
        "fetch-dataset",
        "compute_uk_event",
        "HUGGING_FACE_TOKEN",
        "secrets",
        "gh pr merge",
        "gh workflow run",
        "--auto",
        "--admin",
        "upload-artifact",
    ):
        assert forbidden not in script, forbidden
    # Branches it writes are its own; main is never pushed.
    pushes = [
        line
        for line in script.splitlines()
        if re.search(r"\bgit\b.* push ", line) and not line.lstrip().startswith("#")
    ]
    assert len(pushes) == 2
    assert all("refs/heads/$branch" in line for line in pushes)
    tree = ast.parse((ROOT / "pipeline/uk_replay_results_pr.py").read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        assert not {name.split(".")[0] for name in names} & {
            "policyengine",
            "policyengine_uk",
            "policyengine_core",
            "subprocess",
            "huggingface_hub",
        }
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "__import__"}


def test_every_guard_runs_before_the_commit_or_the_push_it_protects():
    # Defense in depth that correct code never trips (scope) still has to be
    # wired in, in this order.
    lines = SCRIPT.read_text().splitlines()

    def at(fragment):
        found = [
            i
            for i, line in enumerate(lines)
            if fragment in line and not line.lstrip().startswith("#")
        ]
        assert found, fragment
        return found[0]

    assert (
        at("uk_replay_output_guard.py")
        < at("builder check ")
        < at('git merge-base --is-ancestor "$receipt_commit"')
        < at('| tar -x -C "$TREE" --strip-components=3')
        < at("builder apply ")
        < at('git -C "$TREE" add -A')
        < at("builder scope ")
        < at("commit -q -F")
        < at('if [ "$expected" != "$committed" ]')
        < at('pipeline.uk_replay_qualify verify-sealed "$(plan paths namespace)"')
        < at("uk_replay_regenerate.sh")
        < at("scorecard_db.build_db")
        < at('git -C "$TREE" push -q origin')
        < at("gh pr create")
    )


def test_the_control_environment_installs_what_the_builder_imports():
    line = next(
        line for line in SCRIPT.read_text().splitlines() if line.startswith("CONTROL=")
    )
    installed = {
        word.split("==")[0]
        for word, before in zip(line.split()[1:], line.split())
        if before == "--with"
    }
    # The distributions behind every module the builder (and the qualifier it
    # reads latest_certified from) loads, as this environment resolves them.
    probe = subprocess.run(
        [
            sys.executable,
            "-c",
            "import importlib.metadata, sys\n"
            "import pipeline.uk_replay_results_pr, pipeline.uk_replay_qualify\n"
            "owners = importlib.metadata.packages_distributions()\n"
            "names = {n.split('.')[0] for n in sys.modules}\n"
            "print('\\n'.join(sorted({d.lower() for n in names for d in owners.get(n, [])})))",
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT)},
        capture_output=True,
        text=True,
        check=True,
    )
    needed = set(probe.stdout.split())
    assert needed <= installed, sorted(needed - installed)
    assert {"numpy", "pyyaml"} <= needed
    assert not {"policyengine", "policyengine-uk", "policyengine-core"} & needed


def test_the_record_job_dispatches_the_results_workflow_only_when_complete():
    script = RECORD.read_text()
    block = script[script.index('if [ "$status" = complete ]') :]
    block = block[: block.index("\nfi\n") + 4]
    assert "gh workflow run uk-replay-results.yml" in block
    assert '-f request_id="$REQUEST_ID"' in block
    assert '--ref "$DRAIN_REF"' in block
    # A failed dispatch warns and the queue continues.
    assert "::warning::" in block
    assert script.index(block) > script.index('push_state "Status for')
    replay = yaml.safe_load((ROOT / ".github/workflows/uk-replay.yml").read_text())
    assert replay["jobs"]["record"]["permissions"] == {
        "contents": "write",
        "actions": "write",
    }


def test_ci_runs_on_the_pull_request_itself():
    # The bot's pull request gets ordinary pull_request checks (the App token
    # starts them); CI needs, and has, no dispatch trigger for it.
    ci = yaml.safe_load((ROOT / ".github/workflows/ci.yml").read_text())
    assert set(ci[True]) == {"pull_request", "push"}
    assert ci[True]["push"] == {"branches": ["main"]}


# --- the edits, checked against the hand-built results PRs --------------------


def plan_for(variant_id, *, completed="2026-10-16T05:55:28Z", compare_to=None):
    record = committed_record(variant_id)
    receipt = committed_receipt(variant_id)
    return {
        "kind": "released_bundle",
        "request_id": record["qualification_request_sha256"],
        "receipt_sha256": receipt["receipt_sha256"],
        "receipt_commit": {"pe6.4.1": "484eaa7", "pe6.5.0": "19a9ccd"}[variant_id[:7]]
        + "0" * 33,
        "completed_at": completed,
        "compare_to": compare_to or "latest_certified",
        "legacy_variant": rv.load_document()["default_variant"],
    }


@pytest.mark.parametrize("variant_id", [PE641])
def test_the_note_reproduces_the_hand_written_one(variant_id):
    record = committed_record(variant_id)
    written = record.pop("note")
    assert builder.note(record, plan_for(variant_id)) == written


@pytest.mark.parametrize("variant_id", [PE641, PE650])
def test_appending_a_record_reproduces_the_committed_index(variant_id):
    raw = rv.VARIANTS_PATH.read_bytes()
    document = json.loads(raw)
    ids = [v["variant_id"] for v in document["variants"]]
    keep = ids.index(variant_id)
    record = document["variants"][keep]
    before = {**document, "variants": document["variants"][:keep]}
    after = {**document, "variants": document["variants"][: keep + 1]}
    without_note = {k: v for k, v in record.items() if k != "note"}
    assert builder.append_variant(
        canonical_bytes(before), without_note, record["note"]
    ) == canonical_bytes(after)
    with pytest.raises(builder.Refused, match="not canonical"):
        builder.append_variant(json.dumps(before).encode(), without_note, "n")


def test_the_matrix_edit_reproduces_the_committed_ci_workflow():
    text = (ROOT / builder.CI).read_text()
    line = f"          - {PE650}\n"
    assert text.count(line) == 1
    certified = [
        v["variant_id"]
        for v in rv.load_document()["variants"]
        if v["status"] == "certified"
    ]
    assert builder.add_matrix_variant(text.replace(line, ""), PE650, certified) == text
    with pytest.raises(builder.Refused, match="every certified variant"):
        builder.add_matrix_variant(text.replace(line, ""), PE650, certified[:-1])
    with pytest.raises(builder.Refused, match="exactly one"):
        builder.add_matrix_variant(text + text, PE650, certified)


def test_the_test_edits_move_newest_and_extend_committed():
    for name in builder.NEWEST_TESTS:
        text = (ROOT / name).read_text()
        moved = builder.replace_newest(text, PE650, "pe9.9.9_x", name=name)
        assert moved.count('NEWEST = "pe9.9.9_x"') == 1
        assert builder.replace_newest(moved, "pe9.9.9_x", PE650, name=name) == text
        with pytest.raises(builder.Refused, match="not the newest certified"):
            builder.replace_newest(text, PE641, "pe9.9.9_x", name=name)
    text = (ROOT / builder.COMMITTED_TEST).read_text()
    line = f'    "{PE650}",\n'
    assert text.count(line) == 1
    assert (
        builder.append_committed(
            text.replace(line, ""), PE641, PE650, name=builder.COMMITTED_TEST
        )
        == text
    )
    with pytest.raises(builder.Refused, match="does not end with"):
        builder.append_committed(text, PE641, "x", name=builder.COMMITTED_TEST)
    with pytest.raises(builder.Refused, match="exactly once"):
        builder.append_committed("", PE650, "x", name=builder.COMMITTED_TEST)


def test_the_paragraph_states_what_the_hand_written_6_5_0_one_counted():
    paragraph = builder.paragraph(
        committed_record(PE650), committed_receipt(PE650), plan_for(PE650)
    )
    text = flat(paragraph)
    # The integrity and grid sentence is the hand-written one, word for word.
    sentence = (
        "Integrity is complete with no failures, and all six events have "
        "complete supported grids and no inert measure-years."
    )
    assert sentence in text
    assert sentence in flat((ROOT / builder.DOC).read_text())
    assert f"Its release diff is against `{PE641}`" in text
    assert "That diff flags eight rows" in text
    assert "construction 6 and numerical 3, and every other flag count is zero" in text
    assert "request `d83eaf59…`, receipt SHA-256 `a7a67c26…`" in text
    assert "`replay-state` commit `19a9ccd`" in text
    assert all(len(line) <= 76 or " " not in line for line in paragraph.split("\n"))
    legacy = flat(
        builder.paragraph(
            committed_record(PE641), committed_receipt(PE641), plan_for(PE641)
        )
    )
    assert "against the legacy variant `pe5.0.2" in legacy
    assert "coverage 1,513" in legacy


def test_the_paragraph_closes_the_committed_results_subsection():
    text = (ROOT / builder.DOC).read_text()
    edited = builder.insert_paragraph(text, "NEW PARAGRAPH")
    section = edited[edited.index(builder.SECTION) :]
    section = section[: section.index("\n## ")]
    assert section.endswith(
        "real replay of this variant compares whole bytes.\n\nNEW PARAGRAPH\n"
    )
    assert edited.replace("NEW PARAGRAPH\n\n", "", 1) == text
    with pytest.raises(builder.Refused, match="exactly one"):
        builder.insert_paragraph(text.replace(builder.SECTION, "### Other"), "x")


flag_names = st.sampled_from(
    [
        "construction",
        "coverage",
        "inertness",
        "mapping",
        "numerical",
        "structural",
        "support",
    ]
)


@settings(max_examples=150, deadline=None)
@given(
    st.dictionaries(flag_names, st.integers(0, 5000), min_size=1),
    st.integers(0, 40),
    st.lists(st.tuples(st.booleans(), st.integers(0, 3)), min_size=1, max_size=8),
    st.sampled_from(["complete", "incomplete"]),
)
def test_the_paragraph_states_every_nonzero_count_and_no_zero_one(
    counts, rows, grids, integrity
):
    receipt = copy.deepcopy(committed_receipt(PE650))
    receipt["diff"]["flag_counts"] = counts
    receipt["diff"]["flagged_rows"] = [{}] * rows
    receipt["integrity"]["status"] = integrity
    receipt["corpus"]["events"] = {
        f"e{i}": {
            "full_supported_grid_complete": complete,
            "inert_measure_years": [{}] * inert,
        }
        for i, (complete, inert) in enumerate(grids)
    }
    text = flat(builder.paragraph(committed_record(PE650), receipt, plan_for(PE650)))
    for flag, n in counts.items():
        assert (f"{flag} {n:,}" in text) == (n > 0), (flag, n)
    assert f"Integrity is {integrity} with no failures" in text
    complete = sum(c for c, _ in grids)
    inert = sum(i for _, i in grids)
    if complete == len(grids) and not inert:
        assert "events have complete supported grids and no inert" in text
    else:
        assert (
            f"{builder.number(complete)} of {builder.number(len(grids))} events" in text
        )


@settings(max_examples=100, deadline=None)
@given(
    st.lists(
        st.dictionaries(
            st.text(min_size=1, max_size=6),
            st.one_of(st.integers(), st.text(max_size=6), st.booleans(), st.none()),
            max_size=4,
        ),
        max_size=4,
    ),
    st.dictionaries(st.text(min_size=1, max_size=6), st.integers(), max_size=4),
    st.text(max_size=30),
)
def test_the_index_only_grows_by_one_record_in_canonical_form(existing, record, text):
    document = {"schema_version": 1, "default_variant": "x", "variants": existing}
    raw = builder.append_variant(canonical_bytes(document), record, text)
    assert raw == canonical_bytes(json.loads(raw))
    after = json.loads(raw)
    assert after["variants"][:-1] == existing
    assert after["variants"][-1] == {**record, "note": text}
    assert {k: v for k, v in after.items() if k != "variants"} == {
        k: v for k, v in document.items() if k != "variants"
    }


variant_ids = st.from_regex(
    r"pe[0-9]\.[0-9]{1,2}\.[0-9]_[a-z0-9.-]{1,12}", fullmatch=True
)


@settings(max_examples=100, deadline=None)
@given(st.lists(variant_ids, min_size=1, max_size=6, unique=True), variant_ids)
def test_the_matrix_gains_exactly_the_new_variant(existing, new):
    if new in existing:
        return
    text = (
        "on:\n  push:\njobs:\n  replay-engine:\n    strategy:\n      matrix:\n"
        "        variant:\n"
        + "".join(f"          - {v}\n" for v in existing)
        + "    steps:\n      - run: echo\n"
    )
    edited = builder.add_matrix_variant(text, new, [*existing, new])
    matrix = yaml.safe_load(edited)["jobs"]["replay-engine"]["strategy"]["matrix"]
    assert matrix["variant"] == [*existing, new]


EXTRACTED = [
    "results/uk/replays/v/a.json",
    "results/uk/replays/diffs/b__v/DIFF.json",
    "docs/uk_replay/requirements/v.txt",
]


@settings(max_examples=100, deadline=None)
@given(
    st.sets(st.sampled_from(EXTRACTED)),
    st.sets(st.sampled_from(builder.EDITED)),
    st.sets(
        st.sampled_from(
            ["README.md", "results/uk/replays/w/a.json", "results/uk/events/x.json"]
        )
    ),
)
def test_a_commit_touches_the_results_and_the_edits_only(extracted, edited, other):
    plan = {
        "paths": {
            "namespace": "results/uk/replays/v",
            "diff": "results/uk/replays/diffs/b__v",
            "requirements": "docs/uk_replay/requirements/v.txt",
        }
    }
    changed = sorted(extracted | edited | other)
    if not other and edited == set(builder.EDITED):
        builder.scope(plan, changed)
    else:
        with pytest.raises(builder.Refused):
            builder.scope(plan, changed)


# --- the whole builder on a local bare remote ----------------------------------

VERSION = "6.6.0"


def released_request(version=VERSION):
    request = json.loads(
        (
            ROOT / "tests/fixtures/uk_replay/qualification_request_golden.json"
        ).read_text()
    )
    request["kind"] = "released_bundle"
    request["attempt"] = 1
    request["candidate"]["policyengine"].update(
        version=version, source={"pypi": {"wheel_sha256": "a" * 64}}
    )
    bundle = request["candidate"]["expected_release_bundle"]
    bundle.update(bundle_id=f"uk-{version}", policyengine_version=version)
    request["requested_by"] = {
        "repository": REPOSITORY,
        "commit": "b" * 40,
        "trigger": "results pull request test",
    }
    interface.validate_request(request)
    return request


def certified_results(
    directory, *, version=VERSION, status="certified", integrity="complete", extra=None
):
    """A sealed, certified qualification of a synthetic release in
    ``directory`` (a replay-state checkout): request, receipt and results
    exactly as the receiver writes them, before STATUS.json is terminal."""
    request = released_request(version)
    rid = interface.request_id(request)
    record = committed_record(PE650)
    record.pop("note")
    identity = record["identity"]
    identity["packages"]["policyengine"]["version"] = version
    identity["release_bundle"].update(
        bundle_id=f"uk-{version}", policyengine_version=version
    )
    freeze = (ROOT / record["requirements"]["path"]).read_text()
    assert freeze.count("policyengine==6.5.0\n") == 1
    freeze = freeze.replace("policyengine==6.5.0\n", f"policyengine=={version}\n")
    variant_id = rv.variant_slug(identity)
    identity["requirements_sha256"] = hashlib.sha256(freeze.encode()).hexdigest()
    record.update(
        variant_id=variant_id,
        identity_sha256=rv.identity_sha256(identity),
        result_root=f"{rv.REPLAY_RESULT_ROOT}/{variant_id}",
        status=status,
        qualification_request_sha256=rid,
        requirements={
            "path": f"docs/uk_replay/requirements/{variant_id}.txt",
            "sha256": identity["requirements_sha256"],
        },
    )
    request_dir = directory / "requests" / rid
    results = request_dir / "results"
    (results / record["requirements"]["path"]).parent.mkdir(parents=True)
    (results / record["requirements"]["path"]).write_text(freeze)
    rv.validate_record(record, root=results)
    namespace = results / record["result_root"]
    (namespace / "autumn_budget_2024").mkdir(parents=True)
    (namespace / "autumn_budget_2024/RUN_MANIFEST.json").write_text("{}\n")
    (namespace / "SUMMARY.md").write_text("# summary\n")
    diff_dir = results / rv.REPLAY_RESULT_ROOT / "diffs" / f"{PE650}__{variant_id}"
    (diff_dir / "packets").mkdir(parents=True)
    (diff_dir / "DIFF.json").write_text('{"flag_counts": {}}\n')
    (diff_dir / "DIFF.md").write_text("# diff\n")
    (diff_dir / "packets/a.json").write_text("{}\n")
    for relative, contents in (extra or {}).items():
        (results / relative).parent.mkdir(parents=True, exist_ok=True)
        (results / relative).write_bytes(contents)
    manifest = qualify.canonical_bytes(
        qualify.namespace_manifest(namespace, diff_dir=diff_dir)
    )
    (namespace / qualify.MANIFEST_NAME).write_bytes(manifest)
    receipt = committed_receipt(PE650)
    receipt.update(
        request_id=rid,
        variant_id=variant_id,
        variant_identity_sha256=record["identity_sha256"],
    )
    receipt["execution"].update(
        packages=identity["packages"],
        release_bundle=identity["release_bundle"],
        requirements_sha256=identity["requirements_sha256"],
    )
    receipt["results"].update(
        path=f"requests/{rid}/results/", manifest_sha256=qualify.sha256_bytes(manifest)
    )
    receipt["diff"].update(
        base_variant_id=PE650,
        diff_sha256=qualify.sha256_bytes((diff_dir / "DIFF.json").read_bytes()),
    )
    receipt["integrity"]["status"] = integrity
    sealed = interface.seal_receipt(receipt)
    interface.validate(sealed, interface.RECEIPT_SCHEMA_ID)
    payload = qualify.canonical_bytes(sealed)
    (namespace / rv.RECEIPT_NAME).write_bytes(payload)
    (request_dir / rv.RECEIPT_NAME).write_bytes(payload)
    (request_dir / "REQUEST.json").write_bytes(qualify.canonical_bytes(request))
    (results / "VARIANT.json").write_bytes(qualify.canonical_bytes(record))
    assert not qualify.verify_sealed(namespace, diff_dir=diff_dir)
    return rid, record, sealed


def terminal_status(directory, rid, receipt, commit, status="complete"):
    document = {
        "schema": interface.STATUS_SCHEMA_ID,
        "request_id": rid,
        "status": status,
        "history": [
            {"status": "queued", "at": "2026-10-17T05:15:40Z", "run_url": RUN},
            {"status": "running", "at": "2026-10-17T05:16:00Z", "run_url": RUN},
            {"status": status, "at": "2026-10-17T05:55:28Z", "run_url": RUN},
        ],
        "receipt_sha256": receipt["receipt_sha256"],
        "receipt_commit": commit,
    }
    interface.validate(document, interface.STATUS_SCHEMA_ID)
    (directory / "requests" / rid / "STATUS.json").write_bytes(
        qualify.canonical_bytes(document)
    )


REGENERATE_STUB = """#!/usr/bin/env bash
set -euo pipefail
echo "regenerate $(git rev-parse HEAD)" >> "$CHECK_LOG"
if [ "${REGENERATE_FAILS:-}" = 1 ]; then
  echo "replay regeneration changed committed bytes or created untracked files" >&2
  exit 1
fi
"""
BUILD_STUB = """import json, os, sys
from pathlib import Path
with open(os.environ["CHECK_LOG"], "a") as log:
    log.write(f"build_db {sys.argv[1]}\\n")
if os.environ.get("BUILD_DRIFT"):
    Path("data/uk/replay_variants.json").write_text("{}")
suffix = sys.argv[1][-4:] if os.environ.get("BUILD_NONDETERMINISTIC") else ""
print(json.dumps({"content_hash": "c" * 64 + suffix}))
"""
GH_STUB = """import json, os, sys
args = sys.argv[1:]
with open(os.environ["GH_LOG"], "a") as log:
    log.write(json.dumps(args) + "\\n")
if args[:2] == ["pr", "list"]:
    print(os.environ.get("GH_OPEN_PR", ""))
elif args[:2] == ["pr", "create"]:
    print("https://github.com/PolicyEngine/policyengine-scorecard/pull/999")
elif args[:2] != ["pr", "edit"]:
    sys.exit(97)
"""


class Remote:
    """A main branch holding what the builder reads, a replay-state branch
    and a bare remote, all local; GitHub is a stub that logs its calls."""

    def __init__(self, tmp_path):
        self.tmp = tmp_path
        self.seed = tmp_path / "seed"
        self.seed.mkdir()
        git(self.seed, "init", "-q", "-b", "main")
        for key, value in (("user.name", "Test"), ("user.email", "test@example.org")):
            git(self.seed, "config", key, value)
        ignore = shutil.ignore_patterns("__pycache__")
        shutil.copytree(ROOT / "pipeline", self.seed / "pipeline", ignore=ignore)
        shutil.copytree(ROOT / ".github", self.seed / ".github")
        for relative in (
            "docs/uk_replay/schemas",
            "docs/uk_replay/requirements",
        ):
            shutil.copytree(ROOT / relative, self.seed / relative)
        for relative in (
            builder.INDEX,
            builder.DOC,
            builder.COMMITTED_TEST,
            *builder.NEWEST_TESTS,
            "data/uk/certified_bundle.json",
            "docs/uk_replay/requirements.txt",
        ):
            (self.seed / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / relative, self.seed / relative)
        (self.seed / ".github/scripts/uk_replay_regenerate.sh").write_text(
            REGENERATE_STUB
        )
        (self.seed / "scorecard_db").mkdir()
        (self.seed / "scorecard_db/__init__.py").write_text("")
        (self.seed / "scorecard_db/build_db.py").write_text(BUILD_STUB)
        shutil.copyfile(ROOT / ".gitignore", self.seed / ".gitignore")
        git(self.seed, "add", ".")
        git(self.seed, "commit", "-qm", "Main")
        self.state = tmp_path / "state"
        self.state.mkdir()
        git(self.state, "init", "-q", "-b", "replay-state")
        for key, value in (("user.name", "Test"), ("user.email", "test@example.org")):
            git(self.state, "config", key, value)
        git(self.state, "commit", "--allow-empty", "-qm", "Queue")
        self.remote = tmp_path / "remote.git"
        subprocess.run(
            ["git", "clone", "-q", "--bare", str(self.seed), str(self.remote)],
            check=True,
        )
        self.publish_state()
        self.runner = tmp_path / "runner"
        subprocess.run(
            ["git", "clone", "-q", str(self.remote), str(self.runner)], check=True
        )
        self.tools = tmp_path / "bin"
        self.tools.mkdir()
        uv = self.tools / "uv"
        uv.write_text(
            f"#!{sys.executable}\nimport os, sys\nargs = sys.argv[1:]\n"
            "assert args[0] == 'run' and 'python' in args, args\n"
            "assert 'venv' not in args and 'pip' not in args, args\n"
            f"os.execv({sys.executable!r}, [{sys.executable!r}, "
            "*args[args.index('python') + 1:]])\n"
        )
        gh = self.tools / "gh"
        gh.write_text(f"#!{sys.executable}\n{GH_STUB}")
        for tool in (uv, gh):
            tool.chmod(0o755)
        self.runs = 0

    def publish_state(self):
        git(self.state, "push", "-q", "-f", str(self.remote), "HEAD:replay-state")

    def certify(self, **kwargs):
        """Record a certified request on replay-state as the recorder does:
        receipt and results first, then the terminal status naming them."""
        status = kwargs.pop("status_value", "complete")
        rid, record, receipt = certified_results(self.state, **kwargs)
        git(self.state, "add", ".")
        git(self.state, "commit", "-qm", f"Receipt for {rid}")
        commit = git(self.state, "rev-parse", "HEAD")
        terminal_status(self.state, rid, receipt, commit, status)
        git(self.state, "add", ".")
        git(self.state, "commit", "-qm", f"Status for {rid}")
        self.publish_state()
        return rid, record, receipt

    def run(self, rid, **overrides):
        self.runs += 1
        temp = self.tmp / f"runner-temp-{self.runs}"
        temp.mkdir()
        self.gh_log = temp / "gh.jsonl"
        self.check_log = temp / "checks.log"
        env = {
            **{k: v for k, v in os.environ.items() if not k.startswith("GITHUB_")},
            "PATH": f"{self.tools}:{os.environ['PATH']}",
            "PYTHONDONTWRITEBYTECODE": "1",
            "REQUEST_ID": rid,
            "STATE_BRANCH": "replay-state",
            "BASE_BRANCH": "main",
            "RUNNER_TEMP": str(temp),
            "GITHUB_REPOSITORY": REPOSITORY,
            "GH_LOG": str(self.gh_log),
            "CHECK_LOG": str(self.check_log),
            **overrides,
        }
        for name in ("PYTHONPATH", "HUGGING_FACE_TOKEN", "HF_TOKEN", "GH_TOKEN"):
            env.pop(name, None)
        if "PYTHONPATH" in overrides:
            env["PYTHONPATH"] = overrides["PYTHONPATH"]
        return subprocess.run(
            ["bash", ".github/scripts/uk_replay_results_pr.sh"],
            cwd=self.runner,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def gh_calls(self):
        if not self.gh_log.exists():
            return []
        return [json.loads(line) for line in self.gh_log.read_text().splitlines()]

    def branch(self, record):
        return git(
            self.remote,
            "rev-parse",
            "--verify",
            "-q",
            f"refs/heads/{builder.BRANCH_PREFIX}{record['variant_id']}",
            check=False,
        )


@pytest.fixture
def remote(tmp_path):
    return Remote(tmp_path)


def test_a_certified_request_becomes_one_bot_commit_and_a_pull_request(remote):
    rid, record, receipt = remote.certify()
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    head = remote.branch(record)
    assert head
    main = git(remote.remote, "rev-parse", "main")
    assert git(remote.remote, "rev-parse", f"{head}^") == main
    assert git(remote.remote, "log", "-1", "--format=%ae", head) == BOT_EMAIL
    message = git(remote.remote, "log", "-1", "--format=%B", head)
    assert message.startswith(f"Certify the policyengine.py {VERSION} replay results")
    assert f"Replay-Request: {rid}" in message.splitlines()
    changed = git(remote.remote, "diff", "--name-only", main, head).splitlines()
    namespace, diff = (
        record["result_root"],
        f"results/uk/replays/diffs/{PE650}__{record['variant_id']}",
    )
    assert set(changed) == {
        *builder.EDITED,
        record["requirements"]["path"],
        *(
            f"{namespace}/{p}"
            for p in (
                "autumn_budget_2024/RUN_MANIFEST.json",
                "SUMMARY.md",
                "NAMESPACE_MANIFEST.json",
                "REPLAY_RECEIPT.json",
            )
        ),
        *(f"{diff}/{p}" for p in ("DIFF.json", "DIFF.md", "packets/a.json")),
    }
    # Byte for byte: each result file has replay-state's blob.
    for path in changed:
        if path in builder.EDITED:
            continue
        assert git(remote.remote, "rev-parse", f"{head}:{path}") == git(
            remote.remote, "rev-parse", f"replay-state:requests/{rid}/results/{path}"
        ), path
    # The index is main's plus VARIANT.json and a note, in canonical form.
    index = git(remote.remote, "show", f"{head}:{builder.INDEX}") + "\n"
    document = json.loads(index)
    assert index.encode() == canonical_bytes(document)
    original = json.loads(git(remote.remote, "show", f"main:{builder.INDEX}"))
    assert document["variants"][:-1] == original["variants"]
    assert document["variants"][-1] == {
        **record,
        "note": (
            f"The {VERSION} released bundle, qualified through the receiver on "
            f"17 October 2026 (request {rid[:8]}, receipt "
            f"{receipt['receipt_sha256'][:8]}); data built with policyengine-uk "
            "2.122.2 and certified for 2.130.1."
        ),
    }
    ci = yaml.safe_load(git(remote.remote, "show", f"{head}:{builder.CI}"))
    assert ci["jobs"]["replay-engine"]["strategy"]["matrix"]["variant"] == [
        v["variant_id"] for v in document["variants"] if v["status"] == "certified"
    ]
    for name in builder.NEWEST_TESTS:
        assert f'NEWEST = "{record["variant_id"]}"' in git(
            remote.remote, "show", f"{head}:{name}"
        )
    assert f'    "{PE650}",\n    "{record["variant_id"]}",\n)' in git(
        remote.remote, "show", f"{head}:{builder.COMMITTED_TEST}"
    )
    doc = git(remote.remote, "show", f"{head}:{builder.DOC}")
    section = doc[doc.index(builder.SECTION) : doc.index("## Version-scoped diagnoses")]
    assert (
        f"`{namespace}/` holds the qualification of policyengine.py {VERSION}"
        in flat(section)
    )
    # Main's checks ran on the commit, and the pull request and CI followed.
    checks = remote.check_log.read_text().splitlines()
    assert checks[0] == f"regenerate {head}"
    assert [line.split()[0] for line in checks[1:]] == ["build_db", "build_db"]
    calls = remote.gh_calls()
    assert [call[:2] for call in calls] == [["pr", "list"], ["pr", "create"]]
    create = calls[1]
    assert create[create.index("--base") + 1] == "main"
    assert (
        create[create.index("--head") + 1]
        == f"uk-replay-results/{record['variant_id']}"
    )
    assert "--draft" not in create
    body = (remote.tmp / "runner-temp-1/results-pr/BODY.md").read_text()
    assert "1 sealed namespace(s) checked" in body
    assert "all 8 committed result files" in body
    assert "axiom: n/a" in body
    assert "Diff vs `" + PE650 + "`" in body
    # The builder never merged and never touched main.
    assert git(remote.remote, "rev-parse", "main") == main


def test_the_same_request_on_the_same_main_pushes_nothing_again(remote):
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    head = remote.branch(record)
    result = remote.run(rid, GH_OPEN_PR="999")
    assert result.returncode == 0, result.stdout + result.stderr
    assert remote.branch(record) == head
    assert "already holds this tree" in result.stdout
    assert [call[:2] for call in remote.gh_calls()] == [["pr", "list"]]
    # A pushed branch whose pull request was never opened gets one.
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert remote.branch(record) == head
    assert [call[:2] for call in remote.gh_calls()] == [
        ["pr", "list"],
        ["pr", "create"],
    ]


def test_a_rerun_after_main_moves_rebuilds_only_its_own_branch(remote):
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    first = remote.branch(record)
    (remote.seed / "NOTES.md").write_text("main moved\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Main moves")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    result = remote.run(rid, GH_OPEN_PR="999")
    assert result.returncode == 0, result.stdout + result.stderr
    second = remote.branch(record)
    assert second != first
    assert git(remote.remote, "rev-parse", f"{second}^") == git(
        remote.remote, "rev-parse", "main"
    )
    assert [call[:2] for call in remote.gh_calls()] == [["pr", "list"], ["pr", "edit"]]
    # A person's commit on the branch is never overwritten.
    person = remote.tmp / "person"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(person)], check=True)
    git(person, "switch", "-q", f"uk-replay-results/{record['variant_id']}")
    for key, value in (
        ("user.name", "Reviewer"),
        ("user.email", "reviewer@example.org"),
    ):
        git(person, "config", key, value)
    (person / "docs/uk_replay/RELEASE_REPLAY.md").write_text("interpreted\n")
    git(person, "commit", "-qam", "Interpret the flagged rows")
    git(person, "push", "-q", "origin", "HEAD")
    reviewed = remote.branch(record)
    (remote.seed / "NOTES.md").write_text("main moved again\n")
    git(remote.seed, "commit", "-qam", "Main moves again")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    result = remote.run(rid, GH_OPEN_PR="999")
    assert result.returncode == 1
    assert "which this builder did not write" in result.stderr
    assert remote.branch(record) == reviewed


@pytest.mark.parametrize(
    ("setup", "reason"),
    [
        ({"status_value": "failed"}, "is failed, not complete"),
        ({"status": "candidate"}, "only certified variants are committed"),
    ],
)
def test_an_ineligible_request_ends_with_a_notice_and_no_branch(remote, setup, reason):
    rid, record, _ = remote.certify(**setup)
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "::notice::No results pull request" in result.stdout
    assert reason in result.stdout
    assert not remote.branch(record)
    assert remote.gh_calls() == []


def test_a_variant_already_on_main_is_skipped(remote):
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    git(remote.remote, "update-ref", "refs/heads/main", remote.branch(record))
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{record['variant_id']} is already in {builder.INDEX}" in result.stdout


def tamper(remote, rid, record, how):
    """Change what the builder reads, as an inconsistent state would."""
    results = remote.state / "requests" / rid / "results"
    if how == "receipt_digest":
        status = json.loads((results.parent / "STATUS.json").read_bytes())
        status["receipt_sha256"] = "0" * 64
        (results.parent / "STATUS.json").write_bytes(qualify.canonical_bytes(status))
    elif how == "namespace_receipt":
        path = results / record["result_root"] / rv.RECEIPT_NAME
        path.write_bytes(path.read_bytes() + b"\n")
    elif how == "results_after_receipt":
        (results / record["result_root"] / "SUMMARY.md").write_text("changed later\n")
    elif how == "variant_from_another_request":
        variant = json.loads((results / "VARIANT.json").read_bytes())
        variant["qualification_request_sha256"] = "f" * 64
        (results / "VARIANT.json").write_bytes(qualify.canonical_bytes(variant))
    git(remote.state, "commit", "-qam", f"Tamper: {how}")
    remote.publish_state()


@pytest.mark.parametrize(
    ("how", "message"),
    [
        ("receipt_digest", "STATUS.json names another receipt"),
        ("namespace_receipt", "sealed receipt differs"),
        ("results_after_receipt", "differ from receipt commit"),
        ("variant_from_another_request", "built from another request"),
    ],
)
def test_an_inconsistent_request_is_refused_before_any_push(remote, how, message):
    rid, record, _ = remote.certify()
    tamper(remote, rid, record, how)
    result = remote.run(rid)
    assert result.returncode == 1, result.stdout + result.stderr
    assert message in result.stderr
    assert not remote.branch(record)
    assert remote.gh_calls() == []


@pytest.mark.parametrize(
    ("setup", "message"),
    [
        (
            {"extra": {"results/uk/events/autumn_budget_2024/x.json": b"{}"}},
            "outside the namespace, its diff and its freeze",
        ),
        ({"extra": {"VARIANT2.json": b"{}"}}, "outside the namespace"),
        (
            {"extra": {"results/uk/replays/diffs/x.h5": b"\x89HDF"}},
            "refusing to publish",
        ),
        ({"version": "6.4.9"}, "older than the newest certified 6.5.0"),
    ],
)
def test_results_outside_the_contract_are_refused(remote, setup, message):
    rid, record, _ = remote.certify(**setup)
    result = remote.run(rid)
    assert result.returncode == 1, result.stdout + result.stderr
    assert message in result.stdout + result.stderr
    assert not remote.branch(record)


def test_a_result_file_main_would_ignore_fails_the_byte_identity_check(remote):
    # main's .gitignore ignores dist/: `git add -A` would leave this sealed
    # file out, and the commit would no longer be replay-state's bytes.
    variant_id = f"pe{VERSION}_uk2.130.1_policyengine-uk-data-1.58.1"
    rid, record, _ = remote.certify(
        extra={f"results/uk/replays/{variant_id}/dist/a.json": b"{}\n"}
    )
    assert record["variant_id"] == variant_id
    result = remote.run(rid)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "the committed results are not replay-state's bytes" in result.stderr
    assert not remote.branch(record)


def test_a_path_main_already_holds_or_a_changed_test_shape_is_refused(remote):
    rid, record, _ = remote.certify()
    path = remote.seed / record["requirements"]["path"]
    path.write_text("already here\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Collide")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    result = remote.run(rid)
    assert result.returncode == 1
    assert f"main already holds {record['requirements']['path']}" in result.stderr
    git(remote.seed, "rm", "-q", record["requirements"]["path"])
    test = remote.seed / builder.NEWEST_TESTS[0]
    test.write_text(test.read_text().replace("NEWEST = ", "LATEST = "))
    git(remote.seed, "commit", "-qam", "Reshape a test")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    result = remote.run(rid)
    assert result.returncode == 1
    assert "must define NEWEST exactly once" in result.stderr
    assert not remote.branch(record)


@pytest.mark.parametrize(
    ("override", "message"),
    [
        ({"REGENERATE_FAILS": "1"}, "replay regeneration changed committed bytes"),
        ({"BUILD_NONDETERMINISTIC": "1"}, "nondeterministic"),
        ({"BUILD_DRIFT": "1"}, "changed tracked files"),
    ],
)
def test_a_failed_check_stops_before_the_push(remote, override, message):
    rid, record, _ = remote.certify()
    result = remote.run(rid, **override)
    assert result.returncode == 1, result.stdout + result.stderr
    assert message in result.stderr
    assert not remote.branch(record)
    assert remote.gh_calls() == []


def test_an_incomplete_integrity_opens_a_draft(remote):
    rid, record, _ = remote.certify(integrity="incomplete")
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    create = next(call for call in remote.gh_calls() if call[:2] == ["pr", "create"])
    assert "--draft" in create
    body = (remote.tmp / "runner-temp-1/results-pr/BODY.md").read_text()
    assert "this pull request is a draft" in body


def test_a_malformed_or_unknown_request_id_fails(remote):
    result = remote.run("../escape")
    assert result.returncode == 1
    assert "64 lowercase hex" in result.stderr
    result = remote.run("e" * 64)
    assert result.returncode == 1
    assert "has no request" in result.stderr


# --- the record job's dispatch ---------------------------------------------------


@pytest.mark.parametrize("dispatch_fails", [False, True])
def test_the_recorder_dispatches_the_results_workflow_for_a_complete_request(
    tmp_path, dispatch_fails
):
    from pipeline import uk_replay_queue as queue

    seed = tmp_path / "state"
    seed.mkdir()
    git(seed, "init", "-q", "-b", "replay-state")
    for key, value in (("user.name", "Test"), ("user.email", "test@example.org")):
        git(seed, "config", key, value)
    request_id, _ = queue.enqueue(
        seed, {"invalid": "request"}, run_url=RUN, now="2026-10-17T00:00:00Z"
    )
    queue.set_status(
        seed, request_id, "running", run_url=RUN, now="2026-10-17T01:00:00Z"
    )
    git(seed, "add", ".")
    git(seed, "commit", "-qm", "Running")
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(remote)], check=True)
    runner = tmp_path / "runner"
    subprocess.run(["git", "clone", "-q", str(remote), str(runner)], check=True)
    git(runner, "switch", "-q", "--detach")
    for relative in ("pipeline/uk_replay_queue.py", "pipeline/uk_replay_interface.py"):
        (runner / relative).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, runner / relative)
    shutil.copytree(ROOT / "docs/uk_replay/schemas", runner / "docs/uk_replay/schemas")
    shutil.copytree(ROOT / ".github/scripts", runner / ".github/scripts")
    receipt = committed_receipt(PE650)
    receipt.update(request_id=request_id)
    receipt["results"]["path"] = f"requests/{request_id}/results/"
    receipt = interface.seal_receipt(receipt)
    uploaded = runner / "output/state/requests" / request_id
    (uploaded / "results").mkdir(parents=True)
    (uploaded / "results/VARIANT.json").write_text("{}\n")
    (uploaded / rv.RECEIPT_NAME).write_bytes(qualify.canonical_bytes(receipt))
    (runner / "output/outcome.json").write_text(
        json.dumps({"status": "complete", "receipt_sha256": receipt["receipt_sha256"]})
    )
    tools = tmp_path / "bin"
    tools.mkdir()
    (tools / "uv").write_text(
        f"#!{sys.executable}\nimport os, sys\nargs = sys.argv[1:]\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, "
        "*args[args.index('python') + 1:]])\n"
    )
    log = tmp_path / "gh.jsonl"
    (tools / "gh").write_text(
        f"#!{sys.executable}\nimport json, sys\n"
        f"open({str(log)!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
        f"sys.exit({1 if dispatch_fails else 0})\n"
    )
    for tool in tools.iterdir():
        tool.chmod(0o755)
    result = subprocess.run(
        ["bash", ".github/scripts/uk_replay_record.sh"],
        cwd=runner,
        env={
            **os.environ,
            "PATH": f"{tools}:{os.environ['PATH']}",
            "PYTHONPATH": str(runner),
            "STATE_BRANCH": "replay-state",
            "RUNNER_TEMP": str(tmp_path),
            "RUN_URL": RUN,
            "REQUEST_ID": request_id,
            "GITHUB_REPOSITORY": REPOSITORY,
            "DRAIN_REF": "main",
        },
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    assert status["status"] == "complete"
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    # The results workflow, after the terminal status; the queue is empty.
    assert calls == [
        [
            "workflow",
            "run",
            "uk-replay-results.yml",
            "--repo",
            REPOSITORY,
            "--ref",
            "main",
            "-f",
            f"request_id={request_id}",
        ]
    ]
    assert ("could not start the results workflow" in result.stdout) == dispatch_fails


def test_no_branch_name_or_path_the_builder_writes_escapes_its_prefix():
    # Variant ids come from identities; the branch and paths are built from
    # them alone and must stay inside their prefixes.
    record = committed_record(PE650)
    paths = builder.result_paths(record, committed_receipt(PE650))
    assert paths["namespace"] == f"results/uk/replays/{PE650}"
    assert paths["diff"] == f"results/uk/replays/diffs/{PE641}__{PE650}"
    assert paths["requirements"] == f"docs/uk_replay/requirements/{PE650}.txt"
    assert re.fullmatch(r"[A-Za-z0-9._-]+", record["variant_id"])
