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
import contextlib
import copy
import difflib
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


CHECKOUT_PIN = "actions/checkout@11d5960a326750d5838078e36cf38b85af677262"
TOKEN_PIN = "actions/create-github-app-token@fee1f7d63c2ff003460e3d139729b119787bc349"


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
    jobs = document["jobs"]
    assert set(jobs) == {"build", "propose"}
    build_job, propose_job = jobs["build"], jobs["propose"]
    # GITHUB_TOKEN reads in both; only the App token, in its own job, writes.
    assert (
        build_job["permissions"] == propose_job["permissions"] == {"contents": "read"}
    )
    assert build_job["if"] == (
        "github.ref == format('refs/heads/{0}', github.event.repository.default_branch)"
    )
    assert propose_job["needs"] == "build"
    assert propose_job["if"] == "needs.build.outputs.action == 'build'"

    # Job 1 runs the checks and their PyPI packages, with no credential.
    checkout, setup, build = build_job["steps"]
    assert checkout["uses"] == "actions/checkout@v4"
    assert checkout["with"] == {"fetch-depth": 0, "persist-credentials": False}
    assert setup["uses"] == "astral-sh/setup-uv@v5"
    assert setup["with"] == {"enable-cache": False}
    assert build["id"] == "build"
    assert build["run"] == "bash .github/scripts/uk_replay_results_pr.sh build"
    assert build["env"] == {
        "REQUEST_ID": "${{ github.event.inputs.request_id }}",
        "STATE_BRANCH": "replay-state",
        "BASE_BRANCH": "${{ github.event.repository.default_branch }}",
    }
    assert "secrets." not in json.dumps(build_job)
    assert set(build_job["outputs"]) == {
        "action",
        "base",
        "state",
        "tree",
        "sealed",
        "content_hash",
    }

    # Job 2, on a fresh runner: no uv, actions pinned to commits, and the
    # token minted only after its own stdlib rebuild matched job 1's tree.
    checkout2, rebuild, token, propose = propose_job["steps"]
    assert checkout2["uses"] == CHECKOUT_PIN
    assert checkout2["with"] == {"fetch-depth": 0, "persist-credentials": False}
    assert rebuild["id"] == "rebuild"
    assert rebuild["run"] == "bash .github/scripts/uk_replay_results_pr.sh rebuild"
    assert rebuild["env"] == {
        "REQUEST_ID": "${{ github.event.inputs.request_id }}",
        "STATE_BRANCH": "replay-state",
        "BASE_BRANCH": "${{ github.event.repository.default_branch }}",
        "BUILT_TREE": "${{ needs.build.outputs.tree }}",
        "BUILT_BASE": "${{ needs.build.outputs.base }}",
        "BUILT_STATE": "${{ needs.build.outputs.state }}",
        "BUILT_SEALED": "${{ needs.build.outputs.sealed }}",
        "BUILT_CONTENT_HASH": "${{ needs.build.outputs.content_hash }}",
    }
    rebuilt = "steps.rebuild.outputs.action == 'build'"
    assert token["if"] == rebuilt and propose["if"] == rebuilt
    assert token["uses"] == TOKEN_PIN
    assert token["id"] == "token"
    assert token["with"] == {
        "app-id": "${{ secrets.APP_ID }}",
        "private-key": "${{ secrets.APP_PRIVATE_KEY }}",
        "permission-contents": "write",
        "permission-pull-requests": "write",
        "permission-workflows": "write",
    }
    steps = [*build_job["steps"], *propose_job["steps"]]
    assert [step for step in steps if "secrets." in json.dumps(step)] == [token]
    assert [step for step in steps if "steps.token" in json.dumps(step)] == [propose]
    assert propose["run"] == "bash .github/scripts/uk_replay_results_pr.sh propose"
    assert propose["env"] == {
        "REQUEST_ID": "${{ github.event.inputs.request_id }}",
        "STATE_BRANCH": "replay-state",
        "BASE_BRANCH": "${{ github.event.repository.default_branch }}",
        "BUILT_COMMIT": "${{ steps.rebuild.outputs.commit }}",
        "BUILT_BRANCH": "${{ steps.rebuild.outputs.branch }}",
        "GH_TOKEN": "${{ steps.token.outputs.token }}",
    }
    for step in steps:
        assert "${{" not in step.get("run", "")
        assert not step.get("uses", "").startswith(("actions/cache", "actions/upload"))
    assert not any("setup-uv" in step.get("uses", "") for step in propose_job["steps"])


def phase(script, name):
    """The body of one function in the builder script."""
    start = script.index(f"\n{name}() {{\n")
    return script[start : script.index("\n}\n", start)]


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
    # Branches it writes are its own; main is never pushed, and every push
    # goes through the one helper that hands git the App token.
    commands = [
        line for line in script.splitlines() if not line.lstrip().startswith("#")
    ]
    pushes = [line for line in commands if "pushgit push" in line]
    assert len(pushes) == 2
    assert all("refs/heads/$branch" in line for line in pushes)
    assert not [line for line in commands if re.search(r"\bgit\b[^#]* push\b", line)]
    # Job 1 holds no token and calls no GitHub API. Job 2, which holds the
    # token, runs git, gh and the standard library: no uv, no PYTHONPATH,
    # and every Python is isolated, the builder without site-packages.
    build, rebuild, propose = (
        phase(script, n) for n in ("build", "rebuild", "propose")
    )
    assemble = phase(script, "assemble")
    for section in (build, assemble):
        assert "GH_TOKEN" not in section and "gh " not in section
    for section in (rebuild, propose, assemble):
        for forbidden in ("uv ", "CONTROL", "PYTHONPATH", "--with"):
            assert forbidden not in section, forbidden
        for line in section.splitlines():
            if "python" in line and not line.lstrip().startswith("#"):
                assert "python3 -I" in line, line
    assert 'python3 -I -S "$HERE/pipeline/uk_replay_results_pr.py"' in rebuild
    # propose runs neither the builder nor any pipeline module. Its messages
    # may name them (review of 78e080c6, 3): only the text of a quoted
    # ::error::, ::notice:: or ::warning:: string with no command
    # substitution is set aside, never the rest of its line, and propose
    # holds no inline comment for a command to hide behind.
    message = re.compile(r'"::(?:error|notice|warning)::(?:[^"$\\`]|\$(?!\())*"')

    def runs_pipeline_code(line):
        command = message.sub('""', line)
        return (
            "#" in command
            or "pipeline" in command
            or bool(re.search(r"\bbuilder\b", command))
        )

    assert runs_pipeline_code('echo "::error::fine" >&2; builder check')
    assert runs_pipeline_code('echo "::notice::$(builder check)"')
    assert runs_pipeline_code("true # builder check")
    assert not runs_pipeline_code('echo "::error::$branch: not this builder\'s" >&2')
    for line in propose.splitlines():
        if not line.lstrip().startswith("#"):
            assert not runs_pipeline_code(line), line
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
    script = SCRIPT.read_text()

    def order(section, *fragments):
        lines = [
            line for line in section.splitlines() if not line.lstrip().startswith("#")
        ]
        positions = []
        for fragment in fragments:
            found = [i for i, line in enumerate(lines) if fragment in line]
            assert found, fragment
            positions.append(found[0])
        assert positions == sorted(positions), fragments

    order(
        phase(script, "assemble"),
        "uk_replay_output_guard.py",
        "builder check ",
        'git merge-base --is-ancestor "$receipt_commit"',
        '| tar -x -C "$TREE" --strip-components=3',
        "builder apply ",
        'git -C "$TREE" add -A',
        "builder scope ",
        "commit -q -F",
        'if [ "$expected" != "$committed" ]',
    )
    order(
        phase(script, "build"),
        "assemble ",
        'verify-sealed "$(plan paths namespace)"',
        "uk_replay_regenerate.sh",
        "scorecard_db.build_db",
        "output tree",
        "output action build",
    )
    rebuild = phase(script, "rebuild")
    order(
        rebuild,
        "the build job's outputs are malformed",
        'git merge-base --is-ancestor "$BUILT_BASE"',
        'git merge-base --is-ancestor "$GITHUB_SHA"',
        "assemble ",
        "not the tree the build job verified",
        'builder check --request-dir "$STAGE/$REQUEST" --checkout "$WORK/tip"',
        "on main as it is now",
        " body ",
        "output action build",
    )
    # Review of 78e080c6 (1): job 2 reads the request only as assemble
    # extracted it, after the output guard; the tip check rereads that copy,
    # never the replay-state tree.
    commands = [
        line for line in rebuild.splitlines() if not line.lstrip().startswith("#")
    ]
    assert not [line for line in commands if "git archive" in line or "tar " in line]
    checks = [line for line in commands if "builder check" in line]
    assert len(checks) == 1 and '--request-dir "$STAGE/$REQUEST"' in checks[0]
    order(
        phase(script, "propose"),
        "the results commit changed after it was assembled",
        "pushgit push -q origin",
        "holds work this builder did not write",
        "pushgit push -q --force-with-lease",
        "gh pr create",
    )


def test_the_control_environment_installs_what_the_builder_imports():
    # The build job's CONTROL runs the builder's strict path and
    # uk_replay_qualify verify-sealed. Their third-party imports, top-level
    # or inside functions, must all be installed; release and dataset code
    # (imported only by the qualifier's run and fetch steps) must not be.
    line = next(
        line.strip().removeprefix("local ")
        for line in SCRIPT.read_text().splitlines()
        if "CONTROL=(" in line
    )
    installed = {
        word.split("==")[0]
        for word, before in zip(line.split()[1:], line.split())
        if before == "--with"
    }
    imported = set()
    for relative in (
        "pipeline/uk_replay_results_pr.py",
        "pipeline/uk_replay_interface.py",
        "pipeline/uk_replay_variants.py",
        "pipeline/uk_replay_qualify.py",
    ):
        for node in ast.walk(ast.parse((ROOT / relative).read_text())):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and not node.level:
                imported.add((node.module or "").split(".")[0])
    third_party = imported - set(sys.stdlib_module_names) - {"pipeline", "__future__"}
    release = {
        "policyengine",
        "policyengine_uk",
        "policyengine_core",
        "huggingface_hub",
    }
    needed = {{"yaml": "pyyaml"}.get(name, name) for name in third_party - release}
    assert needed == {"jsonschema", "rfc8785", "pyyaml"}
    assert installed == needed, sorted(installed ^ needed)
    assert not release & installed


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


def test_the_builders_canonical_form_is_compute_uk_events():
    # The index's canonical form is compute_uk_event.canonical_bytes (a test
    # pins it). The builder keeps its own copy so the job holding the token
    # imports no numpy; the two must agree byte for byte.
    from pipeline.compute_uk_event import canonical_bytes as event_canonical

    document = json.loads(rv.VARIANTS_PATH.read_bytes())
    assert builder.canonical_bytes(document) == event_canonical(document)
    assert builder.canonical_bytes(document) == rv.VARIANTS_PATH.read_bytes()


@settings(max_examples=200, deadline=None)
@given(
    st.recursive(
        st.one_of(
            st.none(),
            st.booleans(),
            st.integers(-(10**18), 10**18),
            st.floats(allow_nan=False, allow_infinity=False),
            st.text(max_size=8),
        ),
        lambda children: st.one_of(
            st.lists(children, max_size=4),
            st.dictionaries(st.text(max_size=6), children, max_size=4),
        ),
        max_leaves=12,
    )
)
def test_both_canonical_forms_agree_on_any_json(value):
    from pipeline.compute_uk_event import canonical_bytes as event_canonical

    assert builder.canonical_bytes(value) == event_canonical(value)


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


# The ci.yml each hand-built results PR edited, byte for byte: #188 (6.4.1)
# edited e796ffb5^'s and #190 (6.5.0) f4164f20^'s. CI's shallow checkout has
# no history, so the files are committed; their git blob ids pin them to
# those commits (`git rev-parse e796ffb5^:.github/workflows/ci.yml`).
RESULTS_PR_FIXTURES = ROOT / "tests/fixtures/uk_replay/results_pr"
HAND_EDITED = {
    PE641: ("ci_before_188.yml", "9a5decd648be594e644443d0ddf020407ced5d03"),
    PE650: ("ci_before_190.yml", "454624d30c1a3e9477a4e0b4a49408e104ff0d2c"),
}
# f4164f20:.github/workflows/ci.yml, #190's result. #188's result (#190's
# input) also changed the determinism step, so only its matrix hunk is ours.
AFTER_190 = "29f7a1b88bb05de435e7174e5ad630c24cb87492"
SYNTHETIC = "pe9.9.9_uk9.9.9_x"


def git_blob(data):
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def hand_edited(variant_id):
    """The ci.yml the hand-built results PR for ``variant_id`` edited, and
    the certified variants once it merged (append order)."""
    name, blob = HAND_EDITED[variant_id]
    data = (RESULTS_PR_FIXTURES / name).read_bytes()
    assert git_blob(data) == blob, name
    certified = [
        v["variant_id"]
        for v in rv.load_document()["variants"]
        if v["status"] == "certified"
    ]
    return data.decode(), certified[: certified.index(variant_id) + 1]


@contextlib.contextmanager
def without_yaml():
    """``import yaml`` fails, as under the propose job's python3 -I -S."""
    saved = sys.modules.get("yaml")
    sys.modules["yaml"] = None
    try:
        yield
    finally:
        if saved is None:
            del sys.modules["yaml"]
        else:
            sys.modules["yaml"] = saved


def changes(before, after):
    """Each change from ``before`` to ``after``: (tag, first line, last
    line, the new lines)."""
    old, new = before.splitlines(True), after.splitlines(True)
    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    return [
        (tag, i1, i2, tuple(new[j1:j2]))
        for tag, i1, i2, j1, j2 in matcher.get_opcodes()
        if tag != "equal"
    ]


@pytest.mark.parametrize("variant_id", [PE641, PE650])
def test_the_stdlib_matrix_edit_is_the_hand_built_one(variant_id):
    # Review of 78e080c6 (3): on the bytes #188 and #190 edited, the propose
    # job's edit, with no yaml importable, is the matrix edit each made by
    # hand. (The strict edit returns the same text once its YAML checks
    # pass; that agreement holds by construction.)
    text, certified = hand_edited(variant_id)
    with without_yaml():
        lean = builder.add_matrix_variant(text, variant_id, certified, strict=False)
        with pytest.raises(ImportError):
            builder.add_matrix_variant(text, variant_id, certified)
    if variant_id == PE650:
        assert git_blob(lean.encode()) == AFTER_190
    else:
        after = (RESULTS_PR_FIXTURES / HAND_EDITED[PE650][0]).read_text()
        ours = changes(text, lean)
        assert ours == [("insert", 85, 85, (f"          - {PE641}\n",))]
        assert ours[0] in changes(text, after)
        assert len(changes(text, after)) == 2
    assert builder.add_matrix_variant(text, variant_id, certified) == lean


def test_the_propose_jobs_interpreter_makes_the_hand_built_edit():
    # python3 -I -S, as the propose job runs the builder: no site-packages,
    # so nothing but the standard library can be imported.
    text, certified = hand_edited(PE650)
    code = (
        "import hashlib, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from pipeline import uk_replay_results_pr as builder\n"
        "text = open(sys.argv[2]).read()\n"
        "edited = builder.add_matrix_variant(\n"
        "    text, sys.argv[3], sys.argv[4:], strict=False\n"
        ").encode()\n"
        "print(hashlib.sha1(b'blob %d\\0' % len(edited) + edited).hexdigest())\n"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            code,
            str(ROOT),
            str(RESULTS_PR_FIXTURES / HAND_EDITED[PE650][0]),
            PE650,
            *certified,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == f"{AFTER_190}\n"


@settings(max_examples=200, deadline=None)
@given(
    st.sampled_from([PE641, PE650]),
    st.data(),
)
def test_the_stdlib_list_check_alone_refuses_a_wrong_matrix(variant_id, data):
    # The propose job skips the YAML checks, so its list check must refuse
    # by itself: the real file with its matrix listing anything other than
    # the certified variants before this one is refused.
    text, certified = hand_edited(variant_id)
    block = "".join(f"          - {v}\n" for v in certified[:-1])
    assert text.count(block) == 1
    listed = data.draw(
        st.one_of(
            st.just(certified[:-1]),
            st.lists(st.sampled_from([*certified, SYNTHETIC]), max_size=6),
        )
    )
    edited = text.replace(block, "".join(f"          - {v}\n" for v in listed), 1)
    with without_yaml():
        if listed == certified[:-1]:
            builder.add_matrix_variant(edited, variant_id, certified, strict=False)
        else:
            with pytest.raises(builder.Refused):
                builder.add_matrix_variant(edited, variant_id, certified, strict=False)


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
        assert (
            "events have complete supported grids and no inert"
            if len(grids) > 1
            else "its one event has a complete supported grid and no inert"
        ) in text
    else:
        assert (
            f"{builder.number(complete)} of {builder.counted(len(grids), 'event')}"
            in text
        )
        assert f"{builder.counted(inert, 'inert measure-year')} in all" in text
    # Agreement in number: never "one rows" or "two row".
    assert not re.search(r"\bone (rows|events|failures|inert measure-years)\b", text)
    words = "zero|two|three|four|five|six|seven|eight|nine|ten"
    assert not re.search(rf"\b({words}) (row|event|failure|inert measure-year)\b", text)


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
    directory,
    *,
    version=VERSION,
    status="certified",
    integrity="complete",
    extra=None,
    data_build_id=None,
    requalify=False,
    other_identity=False,
):
    """A sealed, certified qualification of a synthetic release in
    ``directory`` (a replay-state checkout): request, receipt and results
    exactly as the receiver writes them, before STATUS.json is terminal."""
    if requalify:
        # An exactly certified pair qualified again: the receiver returns the
        # committed record, note and original request digest included.
        version = "6.5.0"
    request = released_request(version)
    rid = interface.request_id(request)
    record = committed_record(PE650)
    identity = record["identity"]
    freeze = (ROOT / record["requirements"]["path"]).read_text()
    variant_id = PE650
    if not requalify:
        record.pop("note")
        identity["packages"]["policyengine"]["version"] = version
        identity["release_bundle"].update(
            bundle_id=f"uk-{version}", policyengine_version=version
        )
        if data_build_id:
            identity["release_bundle"]["certified_data_build_id"] = data_build_id
            record["certification"]["data_build_id"] = data_build_id
        if other_identity:
            # The same versions installed from other bytes: the same slug.
            identity["packages"]["policyengine"]["record_sha256"] = "f" * 64
        assert freeze.count("policyengine==6.5.0\n") == 1
        freeze = freeze.replace("policyengine==6.5.0\n", f"policyengine=={version}\n")
        variant_id = rv.variant_slug(identity)
        identity["requirements_sha256"] = hashlib.sha256(freeze.encode()).hexdigest()
    record.update(
        variant_id=variant_id,
        identity_sha256=rv.identity_sha256(identity),
        result_root=f"{rv.REPLAY_RESULT_ROOT}/{variant_id}",
        status=status,
        qualification_request_sha256=record["qualification_request_sha256"]
        if requalify
        else rid,
        requirements={
            "path": f"docs/uk_replay/requirements/{variant_id}.txt",
            "sha256": identity["requirements_sha256"],
        },
    )
    request_dir = directory / "requests" / rid
    results = request_dir / "results"
    (results / record["requirements"]["path"]).parent.mkdir(parents=True)
    (results / record["requirements"]["path"]).write_text(freeze)
    if not data_build_id:
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
        # python3 is the test interpreter: under -I -S it sees no
        # site-packages, so the stdlib rebuild cannot import a package.
        (self.tools / "python3").symlink_to(sys.executable)
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

    def environment(self, temp, rid, **overrides):
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
        return env

    @staticmethod
    def step(runner, phase, env, outputs=None, **extra):
        if outputs is not None:
            extra["GITHUB_OUTPUT"] = str(outputs)
        result = subprocess.run(
            ["bash", ".github/scripts/uk_replay_results_pr.sh", phase],
            cwd=runner,
            env={**env, **extra},
            capture_output=True,
            text=True,
            check=False,
        )
        values = {}
        if outputs is not None and outputs.exists():
            values = dict(
                line.split("=", 1) for line in outputs.read_text().splitlines()
            )
        return result, values

    def run(self, rid, forge=None, **overrides):
        """As the workflow runs it. Job 1 builds and verifies in this
        runner's checkout. Job 2 runs on a fresh clone with its own temp
        directory: it rebuilds with the standard library and, only when its
        tree is job 1's, proposes with the token. ``forge`` overrides job 1's
        outputs as job 2 receives them."""
        self.runs += 1
        temp = self.tmp / f"runner-temp-{self.runs}"
        temp.mkdir()
        self.gh_log = temp / "gh.jsonl"
        self.check_log = temp / "checks.log"
        env = self.environment(temp, rid, **overrides)
        built, self.outputs = self.step(
            self.runner, "build", env, temp / "build-output.txt"
        )
        self.rebuilt = {}
        if built.returncode or self.outputs.get("action") != "build":
            return built
        fresh = self.tmp / f"job2-{self.runs}"
        subprocess.run(["git", "clone", "-q", str(self.remote), str(fresh)], check=True)
        temp2 = self.tmp / f"runner-temp-{self.runs}-job2"
        temp2.mkdir()
        env2 = self.environment(temp2, rid, **overrides)
        received = {**self.outputs, **(forge or {})}
        self.job2 = (fresh, env2, temp2)
        rebuilt, self.rebuilt = self.step(
            fresh,
            "rebuild",
            env2,
            temp2 / "rebuild-output.txt",
            BUILT_TREE=received["tree"],
            BUILT_BASE=received["base"],
            BUILT_STATE=received["state"],
            BUILT_SEALED=received["sealed"],
            BUILT_CONTENT_HASH=received["content_hash"],
        )
        outs = [built, rebuilt]
        if not rebuilt.returncode and self.rebuilt.get("action") == "build":
            proposed, _ = self.step(
                fresh,
                "propose",
                env2,
                BUILT_COMMIT=self.rebuilt["commit"],
                BUILT_BRANCH=self.rebuilt["branch"],
                GH_TOKEN="app-installation-token",
            )
            outs.append(proposed)
        return subprocess.CompletedProcess(
            outs[-1].args,
            outs[-1].returncode,
            "".join(o.stdout for o in outs),
            "".join(o.stderr for o in outs),
        )

    def body(self):
        return (self.job2[2] / "results-pr/BODY.md").read_text()

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
    # Main's checks ran in job 1 on a commit with exactly the tree job 2
    # pushed, and the pull request followed.
    checks = remote.check_log.read_text().splitlines()
    verified = checks[0].split()[1]
    assert checks[0] == f"regenerate {verified}"
    assert git(remote.runner, "rev-parse", f"{verified}^{{tree}}") == git(
        remote.remote, "rev-parse", f"{head}^{{tree}}"
    )
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
    body = remote.body()
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
    assert "holds work this builder did not write" in result.stderr
    assert remote.branch(record) == reviewed


def test_an_amended_bot_commit_is_a_persons_work(remote):
    # Review of 97c351b9 (2): `git commit --amend` keeps the author and the
    # trailer and changes only the committer; the rerun must not discard it.
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    person = remote.tmp / "person"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(person)], check=True)
    git(person, "switch", "-q", f"uk-replay-results/{record['variant_id']}")
    for key, value in (
        ("user.name", "Reviewer"),
        ("user.email", "reviewer@example.org"),
    ):
        git(person, "config", key, value)
    (person / "docs/uk_replay/RELEASE_REPLAY.md").write_text("interpreted\n")
    git(person, "commit", "-q", "-a", "--amend", "--no-edit")
    assert git(person, "log", "-1", "--format=%ae") == BOT_EMAIL
    git(person, "push", "-q", "-f", "origin", "HEAD")
    amended = remote.branch(record)
    (remote.seed / "NOTES.md").write_text("main moved\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Main moves")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    result = remote.run(rid, GH_OPEN_PR="999")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "holds work this builder did not write" in result.stderr
    assert remote.branch(record) == amended


def test_the_push_never_overwrites_a_branch_that_moved_after_it_was_read(remote):
    # Review of 97c351b9 (6): --force-with-lease, not --force. Someone pushes
    # to the branch between propose reading it and propose pushing.
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    branch = f"uk-replay-results/{record['variant_id']}"
    (remote.seed / "NOTES.md").write_text("main moved\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Main moves")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    racer = remote.tmp / "racer"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(racer)], check=True)
    git(racer, "switch", "-q", branch)
    for key, value in (("user.name", "Racer"), ("user.email", "racer@example.org")):
        git(racer, "config", key, value)
    git(racer, "commit", "-q", "--allow-empty", "-m", "Pushed mid-propose")
    real_git = shutil.which("git")
    wrapper = remote.tools / "git"
    wrapper.write_text(
        f"#!{sys.executable}\n"
        "import os, subprocess, sys\n"
        "args = sys.argv[1:]\n"
        "if any(a.startswith('--force-with-lease') for a in args):\n"
        f"    subprocess.run([{real_git!r}, '-C', {str(racer)!r}, 'push', '-q', 'origin', 'HEAD'], check=True)\n"
        f"os.execv({real_git!r}, [{real_git!r}, *args])\n"
    )
    wrapper.chmod(0o755)
    try:
        result = remote.run(rid, GH_OPEN_PR="999")
    finally:
        wrapper.unlink()
    assert result.returncode != 0, result.stdout + result.stderr
    assert (
        git(remote.remote, "log", "-1", "--format=%s", branch) == "Pushed mid-propose"
    )
    assert ["pr", "edit"] not in [call[:2] for call in remote.gh_calls()]


def test_the_push_hands_git_the_token_only_through_gh(tmp_path):
    # Review of 97c351b9 (6): the credential path the tests' file remote
    # never exercises. git must ask gh, and gh must answer from GH_TOKEN.
    script = SCRIPT.read_text()
    helper = "-c credential.helper= -c 'credential.helper=!gh auth git-credential'"
    assert helper in script
    request = (
        "protocol=https\nhost=github.com\n"
        "path=PolicyEngine/policyengine-scorecard.git\n\n"
    )

    def fill(path):
        return subprocess.run(
            [
                "git",
                "-c",
                "credential.helper=",
                "-c",
                "credential.helper=!gh auth git-credential",
                "credential",
                "fill",
            ],
            input=request,
            env={
                **os.environ,
                "PATH": path,
                "GH_TOKEN": "app-token",
                "GIT_TERMINAL_PROMPT": "0",
                "GIT_CONFIG_NOSYSTEM": "1",
                "HOME": str(tmp_path),
            },
            capture_output=True,
            text=True,
            check=True,
        )

    log = tmp_path / "gh-credential.jsonl"
    stub = tmp_path / "gh-stub-bin"
    stub.mkdir()
    (stub / "gh").write_text(
        f"#!{sys.executable}\nimport json, os, sys\n"
        f"open({str(log)!r}, 'a').write(json.dumps(sys.argv[1:]) + '\\n')\n"
        "sys.stdin.read()\n"
        "print('protocol=https\\nhost=github.com\\nusername=x-access-token')\n"
        "print('password=' + os.environ['GH_TOKEN'])\n"
    )
    (stub / "gh").chmod(0o755)
    assert "password=app-token" in fill(f"{stub}:{os.environ['PATH']}").stdout
    assert json.loads(log.read_text().splitlines()[0]) == [
        "auth",
        "git-credential",
        "get",
    ]
    # The real gh, where installed (the runner image has it), answers from
    # GH_TOKEN without a network call.
    real = shutil.which("gh")
    if real is None:
        pytest.skip("gh is not installed")
    assert (
        "password=app-token" in fill(f"{Path(real).parent}:{os.environ['PATH']}").stdout
    )


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


def test_an_exact_requalification_of_a_committed_pair_is_skipped(remote):
    # W4 may qualify a certified pair again (a determinism check): the
    # receiver then returns the committed record, note included.
    rid, record, _ = remote.certify(requalify=True)
    assert record["variant_id"] == PE650 and "note" in record
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{PE650} is already in {builder.INDEX}" in result.stdout
    assert remote.outputs == {"action": "skip"}
    assert remote.gh_calls() == []


def test_an_id_main_holds_for_another_identity_is_refused_not_skipped(remote):
    # Review of 97c351b9 (3): the digest suffix is added only when main
    # already holds the slug, so two runs that finish before either merges
    # share an id. The second must not be skipped green.
    rid, record, _ = remote.certify(version="6.5.0", other_identity=True)
    assert record["variant_id"] == PE650
    assert record["identity_sha256"] != committed_record(PE650)["identity_sha256"]
    result = remote.run(rid)
    assert result.returncode == 1, result.stdout + result.stderr
    assert f"{PE650} already names another identity" in result.stderr
    assert "action" not in remote.outputs


# Review of 78e080c6 (2): a request whose variant main already holds is the
# same variant when the id and identity agree. Every other field of main's
# record may differ: the note the results pull request added, and whatever a
# later change to the index (a schema migration) adds, drops or reshapes.
COMPARED = ("variant_id", "identity", "identity_sha256", "status")


@pytest.fixture(scope="module")
def requalified(tmp_path_factory):
    """A complete request whose VARIANT.json is the committed 6.5.0 record,
    as the receiver returns it for a pair it already certified."""
    state = tmp_path_factory.mktemp("requalified")
    rid, _, receipt = certified_results(state, requalify=True)
    terminal_status(state, rid, receipt, "0" * 40)
    return state / "requests" / rid, rid


def decide(requalified, edit, *, strict=True):
    """``check`` against a main whose 6.5.0 record ``edit`` changed: the
    skip reason, or the refusal as ``Refused``."""
    directory, rid = requalified
    document = json.loads(rv.VARIANTS_PATH.read_bytes())
    ids = [v["variant_id"] for v in document["variants"]]
    edit(document["variants"][ids.index(PE650)])
    checkout = directory.parent.parent / "main"
    (checkout / builder.INDEX).parent.mkdir(parents=True, exist_ok=True)
    (checkout / builder.INDEX).write_bytes(canonical_bytes(document))
    with pytest.raises(builder.Ineligible) as skipped:
        builder.check(directory, checkout, rid, "0" * 40, strict=strict)
    return str(skipped.value)


def migrate(record):
    record["note"] = "Reworded after the merge."
    record["schema_migration"] = {"from": 1, "to": 2}
    record.pop("qualification_request_sha256")
    record["data_years_evidence"] = {"reshaped": True}


def other_identity(record):
    record["identity"]["packages"]["policyengine"]["record_sha256"] = "f" * 64
    record["identity_sha256"] = rv.identity_sha256(record["identity"])


@pytest.mark.parametrize("strict", [True, False])
@pytest.mark.parametrize(
    ("edit", "refusal"),
    [
        (lambda record: None, None),
        (migrate, None),
        (other_identity, f"{PE650} already names another identity"),
        (
            lambda record: record.update(identity_sha256="f" * 64),
            f"{PE650} already names another identity",
        ),
        (
            lambda record: record.update(status="candidate"),
            f"holds {PE650} as candidate, not certified",
        ),
    ],
)
def test_a_held_variant_is_skipped_only_for_the_same_identity(
    requalified, edit, refusal, strict
):
    if refusal is None:
        assert decide(requalified, edit, strict=strict) == (
            f"{PE650} is already in {builder.INDEX}"
        )
    else:
        with pytest.raises(builder.Refused, match=re.escape(refusal)):
            decide(requalified, edit, strict=strict)


def test_a_variant_whose_digest_is_not_its_identitys_is_refused(tmp_path):
    # The skip rests on identity_sha256, so VARIANT.json's own digest must be
    # its identity's: a record claiming the committed digest for another
    # identity is refused, not skipped.
    rid, record, receipt = certified_results(tmp_path, requalify=True)
    terminal_status(tmp_path, rid, receipt, "0" * 40)
    directory = tmp_path / "requests" / rid
    record["identity"]["packages"]["policyengine"]["record_sha256"] = "f" * 64
    (directory / "results/VARIANT.json").write_bytes(qualify.canonical_bytes(record))
    (tmp_path / "main" / builder.INDEX).parent.mkdir(parents=True)
    shutil.copyfile(rv.VARIANTS_PATH, tmp_path / "main" / builder.INDEX)
    for strict in (True, False):
        with pytest.raises(builder.Refused, match="not its identity's digest"):
            builder.check(directory, tmp_path / "main", rid, "0" * 40, strict=strict)


json_values = st.recursive(
    st.none() | st.booleans() | st.integers(-5, 5) | st.text(max_size=6),
    lambda children: (
        st.lists(children, max_size=3)
        | st.dictionaries(st.text(max_size=5), children, max_size=3)
    ),
    max_leaves=6,
)


@settings(max_examples=60, deadline=None)
@given(
    st.dictionaries(
        st.text(min_size=1, max_size=12).filter(lambda key: key not in COMPARED),
        json_values,
        max_size=4,
    ),
    st.sets(st.sampled_from(sorted(set(committed_record(PE650)) - set(COMPARED)))),
)
def test_any_change_to_the_rest_of_the_record_still_skips(
    requalified, changed, dropped
):
    def edit(record):
        record.update(changed)
        for key in dropped - set(changed):
            record.pop(key)

    assert decide(requalified, edit) == f"{PE650} is already in {builder.INDEX}"


def leaves(value, path=()):
    if isinstance(value, dict):
        for key, child in value.items():
            yield from leaves(child, (*path, key))
    elif isinstance(value, str):
        yield path


IDENTITY_LEAVES = sorted(leaves(committed_record(PE650)["identity"]))


@settings(max_examples=60, deadline=None)
@given(st.sampled_from(IDENTITY_LEAVES), st.text(min_size=1, max_size=8))
def test_any_change_to_the_identity_is_refused(requalified, path, value):
    def edit(record):
        *parents, last = path
        holder = record["identity"]
        for key in parents:
            holder = holder[key]
        if holder[last] == value:
            holder[last] = value + "x"
        else:
            holder[last] = value
        record["identity_sha256"] = rv.identity_sha256(record["identity"])

    with pytest.raises(builder.Refused, match="already names another identity"):
        decide(requalified, edit)


def test_a_variant_id_that_cannot_name_a_branch_is_refused(remote):
    rid, record, _ = remote.certify(data_build_id="data build;x")
    assert record["variant_id"].endswith("_data build;x")
    result = remote.run(rid)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "cannot name a branch and paths" in result.stderr
    assert "action" not in remote.outputs


@pytest.mark.parametrize(
    ("forge", "message"),
    [
        ({"tree": "0" * 40}, "not the tree the build job verified"),
        ({"base": "1" * 40}, "is not on main or replay-state"),
        ({"state": "2" * 40}, "is not on main or replay-state"),
        ({"sealed": "all fine; rm -rf /"}, "outputs are malformed"),
        ({"content_hash": "not hex"}, "outputs are malformed"),
        ({"tree": "abc"}, "outputs are malformed"),
    ],
)
def test_job_2_pushes_only_what_it_rebuilt_and_job_1_verified(remote, forge, message):
    # Job 1's outputs reach the job holding the token as untrusted strings.
    rid, record, _ = remote.certify()
    result = remote.run(rid, forge=forge)
    assert result.returncode == 1, result.stdout + result.stderr
    assert message in result.stderr
    assert not remote.branch(record)
    assert remote.gh_calls() == []


def test_a_base_older_than_the_workflow_commit_is_refused(remote):
    # Review of f7247f19 (3): a consistent older base, forged or stale.
    rid, record, _ = remote.certify()
    old_main = git(remote.remote, "rev-parse", "main")
    (remote.seed / "NOTES.md").write_text("main moved\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Main moves")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    git(remote.runner, "pull", "-q", "--ff-only")
    workflow_commit = git(remote.remote, "rev-parse", "main")
    result = remote.run(rid, forge={"base": old_main}, GITHUB_SHA=workflow_commit)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "older than this workflow's commit" in result.stderr
    assert not remote.branch(record)


def test_a_rerun_after_the_merge_skips_on_mains_tip(remote):
    # Review of f7247f19 (3): job 2 rerun on job 1's old outputs once the
    # results are on main must not open a second pull request.
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    built = dict(remote.outputs)
    git(remote.remote, "update-ref", "refs/heads/main", remote.branch(record))
    fresh = remote.tmp / "rerun-job2"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(fresh)], check=True)
    temp = remote.tmp / "rerun-job2-temp"
    temp.mkdir()
    remote.gh_log = temp / "gh.jsonl"
    rebuilt, values = remote.step(
        fresh,
        "rebuild",
        remote.environment(temp, rid),
        temp / "out.txt",
        BUILT_TREE=built["tree"],
        BUILT_BASE=built["base"],
        BUILT_STATE=built["state"],
        BUILT_SEALED=built["sealed"],
        BUILT_CONTENT_HASH=built["content_hash"],
    )
    assert rebuilt.returncode == 0, rebuilt.stdout + rebuilt.stderr
    assert values == {"action": "skip"}
    assert "on main as it is now" in rebuilt.stdout
    assert f"{record['variant_id']} is already in {builder.INDEX}" in rebuilt.stdout


def test_main_moving_between_the_jobs_still_rebuilds_on_the_verified_base(remote):
    # Job 2 rebuilds on the main job 1 verified, provided that commit is in
    # main's history; main moving in between does not fail the run.
    rid, record, _ = remote.certify()
    temp = remote.tmp / "job1"
    temp.mkdir()
    remote.gh_log, remote.check_log = temp / "gh.jsonl", temp / "checks.log"
    built, outputs = remote.step(
        remote.runner, "build", remote.environment(temp, rid), temp / "out.txt"
    )
    assert built.returncode == 0, built.stdout + built.stderr
    (remote.seed / "NOTES.md").write_text("main moved\n")
    git(remote.seed, "add", ".")
    git(remote.seed, "commit", "-qm", "Main moves")
    git(remote.seed, "push", "-q", str(remote.remote), "HEAD:main")
    assert git(remote.remote, "rev-parse", "main") != outputs["base"]
    fresh = remote.tmp / "job2"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(fresh)], check=True)
    temp2 = remote.tmp / "job2-temp"
    temp2.mkdir()
    rebuilt, values = remote.step(
        fresh,
        "rebuild",
        remote.environment(temp2, rid),
        temp2 / "out.txt",
        BUILT_TREE=outputs["tree"],
        BUILT_BASE=outputs["base"],
        BUILT_STATE=outputs["state"],
        BUILT_SEALED=outputs["sealed"],
        BUILT_CONTENT_HASH=outputs["content_hash"],
    )
    assert rebuilt.returncode == 0, rebuilt.stdout + rebuilt.stderr
    assert values["action"] == "build"
    tree = temp2 / "results-pr/tree"
    assert git(tree, "rev-parse", "HEAD^") == outputs["base"]
    assert git(tree, "rev-parse", "HEAD^{tree}") == outputs["tree"]


def test_propose_pushes_only_the_commit_rebuild_assembled(remote):
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    fresh, env, temp = remote.job2
    pushed = remote.branch(record)
    # A commit appears on top of the rebuilt one before propose runs again.
    git(
        temp / "results-pr/tree",
        "-c",
        "user.name=x",
        "-c",
        "user.email=x@example.org",
        "commit",
        "-q",
        "--allow-empty",
        "-m",
        "later",
    )
    again, _ = remote.step(
        fresh,
        "propose",
        env,
        BUILT_COMMIT=remote.rebuilt["commit"],
        BUILT_BRANCH=remote.rebuilt["branch"],
        GH_TOKEN="app-installation-token",
    )
    assert again.returncode == 1
    assert "changed after it was assembled" in again.stderr
    assert remote.branch(record) == pushed
    # And propose needs rebuild's outputs and the token.
    for missing in ("BUILT_COMMIT", "BUILT_BRANCH", "GH_TOKEN"):
        extra = {
            "BUILT_COMMIT": remote.rebuilt["commit"],
            "BUILT_BRANCH": remote.rebuilt["branch"],
            "GH_TOKEN": "app-installation-token",
        }
        del extra[missing]
        result, _ = remote.step(fresh, "propose", env, **extra)
        assert result.returncode != 0 and missing in result.stderr


def test_a_variant_already_on_main_is_skipped(remote):
    rid, record, _ = remote.certify()
    assert remote.run(rid).returncode == 0
    git(remote.remote, "update-ref", "refs/heads/main", remote.branch(record))
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{record['variant_id']} is already in {builder.INDEX}" in result.stdout
    # Review of 78e080c6 (2): a later change to main's copy of the record (a
    # schema migration) does not turn the merged request's rerun into a
    # refusal.
    person = remote.tmp / "migration"
    subprocess.run(["git", "clone", "-q", str(remote.remote), str(person)], check=True)
    for key, value in (("user.name", "Migrator"), ("user.email", "m@example.org")):
        git(person, "config", key, value)
    document = json.loads((person / builder.INDEX).read_bytes())
    migrate(document["variants"][-1])
    (person / builder.INDEX).write_bytes(canonical_bytes(document))
    git(person, "commit", "-qam", "Migrate the index")
    git(person, "push", "-q", "origin", "HEAD:main")
    result = remote.run(rid)
    assert result.returncode == 0, result.stdout + result.stderr
    assert f"{record['variant_id']} is already in {builder.INDEX}" in result.stdout
    assert remote.outputs == {"action": "skip"}


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
    assert "this pull request is a draft" in remote.body()


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


def test_the_recorder_dispatches_nothing_for_a_failed_request(tmp_path):
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
    receipt = queue.write_failure_receipt(
        tmp_path / "scratch", request_id, code="event_run_failed", detail="failed"
    )
    uploaded = runner / "output/state/requests" / request_id
    uploaded.mkdir(parents=True)
    (uploaded / rv.RECEIPT_NAME).write_text(json.dumps(receipt))
    (runner / "output/outcome.json").write_text(
        json.dumps({"status": "failed", "receipt_sha256": receipt["receipt_sha256"]})
    )
    tools = tmp_path / "bin"
    tools.mkdir()
    (tools / "uv").write_text(
        f"#!{sys.executable}\nimport os, sys\nargs = sys.argv[1:]\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, "
        "*args[args.index('python') + 1:]])\n"
    )
    (tools / "gh").write_text(
        '#!/usr/bin/env bash\necho unexpected gh "$@" >&2\nexit 93\n'
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
    assert "unexpected gh" not in result.stderr
    status = json.loads(
        git(remote, "show", f"replay-state:requests/{request_id}/STATUS.json")
    )
    assert status["status"] == "failed"


def test_no_branch_name_or_path_the_builder_writes_escapes_its_prefix():
    # Variant ids come from identities; the branch and paths are built from
    # them alone and must stay inside their prefixes.
    record = committed_record(PE650)
    paths = builder.result_paths(record, committed_receipt(PE650))
    assert paths["namespace"] == f"results/uk/replays/{PE650}"
    assert paths["diff"] == f"results/uk/replays/diffs/{PE641}__{PE650}"
    assert paths["requirements"] == f"docs/uk_replay/requirements/{PE650}.txt"
    assert re.fullmatch(r"[A-Za-z0-9._-]+", record["variant_id"])
