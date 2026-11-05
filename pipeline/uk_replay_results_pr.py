"""Build the results pull request that commits a certified qualification to main.

When a request on the ``replay-state`` branch reaches terminal status
``complete`` and its ``results/VARIANT.json`` is ``certified``, its sealed
results become one pull request against main, built as
PolicyEngine/policyengine-scorecard#188 (6.4.1) and #190 (6.5.0) were built
by hand, less the ``ci.yml`` matrix entry each added:

1. ``requests/<request_id>/results/{results,docs}``, byte for byte (the
   workflow extracts them with ``git archive``);
2. ``VARIANT.json`` plus a ``note``, appended to
   ``data/uk/replay_variants.json`` in canonical form;
3. the tests that name the newest certified variant, moved to it;
4. a "Committed certified results" paragraph in RELEASE_REPLAY.md from the
   receipt's counts.

CI's ``replay-engine`` matrix is the index's certified variants
(``.github/scripts/uk_replay_engine_matrix.py``), so edit 2 is all CI needs
to replay the variant. The commit touches nothing under ``.github/``, and
the App token that pushes it has no ``workflows`` permission.

``check`` reads the request directory and a checkout of main and decides
whether to build; ``apply`` makes edits 2 to 4 after the extraction;
``scope`` refuses a commit that touches anything else; ``preflight`` reports
CI's format check, suite and no-drift check, which the build job runs on the
commit; ``body`` renders the pull request, a draft when integrity is not
complete or one of those checks fails, and prints whether it is one.
``.github/scripts/uk_replay_results_pr.sh`` does the git work,
the verification, the push and the pull request. Nothing here installs,
imports or runs candidate or release code, and nothing here merges.

With ``--stdlib``, ``check`` skips what needs a third-party package (JSON
Schema and RFC 8785 digests), so the job that holds the App token can rebuild
the same commit under ``python3 -I -S``; ``apply`` needs no package in either
job. The build job runs ``check`` in full on the same inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import textwrap
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline import uk_replay_interface as interface  # noqa: E402
from pipeline import uk_replay_qualify as qualify  # noqa: E402
from pipeline import uk_replay_variants as variants  # noqa: E402

INDEX = "data/uk/replay_variants.json"
DOC = "docs/uk_replay/RELEASE_REPLAY.md"
# Tests whose NEWEST constant names the newest certified variant.
NEWEST_TESTS = (
    "tests/test_uk_replay_qualify.py",
    "tests/test_uk_replay_determinism.py",
)
# The test whose COMMITTED tuple lists every committed variant, oldest first.
COMMITTED_TEST = "tests/test_uk_replay_variants.py"
EDITED = (INDEX, DOC, *NEWEST_TESTS, COMMITTED_TEST)
# Workflows, and the scripts they run: never in a results commit.
UNTOUCHED = ".github/"
SECTION = "### Committed certified results"
BRANCH_PREFIX = "uk-replay-results/"
TRAILER = "Replay-Request"
AXIOM = "axiom: n/a: replay results and the variant index; no policy encoding."

NEWEST = re.compile(r'^NEWEST = "([^"\n]*)"$', re.M)
COMMITTED = re.compile(r"^COMMITTED = \(\n((?:    [^\n]+,\n)+)\)$", re.M)
# A variant id names a branch, paths and CI's matrix legs: plain characters,
# no traversal, and short enough that two ids joined by "__" (the release
# diff's directory) fit one 255-byte path component.
# .github/scripts/uk_replay_engine_matrix.py applies the same rule to every
# id in the index; a test checks they agree.
VARIANT_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
MAX_VARIANT_ID_LENGTH = 120
WORDS = "zero one two three four five six seven eight nine ten".split()


class Ineligible(Exception):
    """The request is not one to commit: the run skips it with a notice."""


class Refused(Exception):
    """The request looks committable but something disagrees: the run fails."""


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Refused(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical_bytes(value: object) -> bytes:
    """compute_uk_event.canonical_bytes, byte for byte (a test checks): the
    index's canonical form, without importing that module's numpy."""
    return (
        json.dumps(value, indent=1, sort_keys=True, allow_nan=False) + "\n"
    ).encode()


def tally(n: int, noun: str) -> str:
    """``n`` in digits with its noun, singular for one."""
    return f"{n:,} {noun if n == 1 else noun + 's'}"


def number(n: int) -> str:
    return WORDS[n] if 0 <= n < len(WORDS) else f"{n:,}"


def counted(n: int, noun: str) -> str:
    """``n`` in words with its noun, singular for one."""
    return f"{number(n)} {noun if n == 1 else noun + 's'}"


def version_key(version: str) -> tuple[int, ...]:
    """Plain final releases only: discovery and W4 dispatch nothing else."""
    need(
        bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+)*", version)),
        f"policyengine version {version!r} is not a plain final release",
    )
    parts = [int(part) for part in version.split(".")]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def plain_variant_id(variant_id: object) -> bool:
    """An id that can name a branch, paths and a CI matrix leg."""
    return (
        isinstance(variant_id, str)
        and len(variant_id) <= MAX_VARIANT_ID_LENGTH
        and VARIANT_ID.fullmatch(variant_id) is not None
        and ".." not in variant_id
    )


def wrapper_version(record: dict) -> str:
    return record["identity"]["packages"]["policyengine"]["version"]


def result_paths(record: dict, receipt: dict) -> dict:
    """Repository paths the request's results add: the sealed namespace, its
    release diff (when the receipt has one) and the requirements freeze."""
    diff = receipt.get("diff")
    return {
        "namespace": record["result_root"],
        "diff": (
            f"{variants.REPLAY_RESULT_ROOT}/diffs/"
            f"{diff['base_variant_id']}__{record['variant_id']}"
            if diff
            else None
        ),
        "requirements": record["requirements"]["path"],
    }


def completed_at(status: dict) -> str:
    entries = [e for e in status["history"] if e["status"] == "complete"]
    need(len(entries) == 1, "STATUS.json must record exactly one completion")
    return entries[0]["at"]


def day(timestamp: str) -> str:
    moment = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    return f"{moment.day} {moment:%B %Y}"


# --- deciding -------------------------------------------------------------------


def check(
    directory: Path,
    checkout: Path,
    request_id: str,
    state_commit: str,
    *,
    strict: bool = True,
) -> dict:
    """The build plan, or Ineligible / Refused.

    ``directory`` is ``requests/<request_id>`` as extracted from replay-state;
    ``checkout`` is a worktree of main before any extraction. ``strict``
    adds the schema and digest checks that need jsonschema and rfc8785."""
    need(
        bool(re.fullmatch(r"[0-9a-f]{64}", request_id)),
        "request_id must be 64 lowercase hex characters",
    )
    need(
        bool(re.fullmatch(r"[0-9a-f]{40}", state_commit)),
        "state_commit must be a full commit id",
    )
    status = json.loads((directory / "STATUS.json").read_bytes())
    if strict:
        interface.validate(status, interface.STATUS_SCHEMA_ID)
    need(status["request_id"] == request_id, "STATUS.json names another request")
    if status["status"] != "complete":
        raise Ineligible(f"request {request_id} is {status['status']}, not complete")
    receipt_bytes = (directory / variants.RECEIPT_NAME).read_bytes()
    receipt = json.loads(receipt_bytes)
    if strict:
        interface.validate(receipt, interface.RECEIPT_SCHEMA_ID)
    need(receipt["request_id"] == request_id, "the receipt names another request")
    need(
        receipt["receipt_sha256"] == status["receipt_sha256"],
        "STATUS.json names another receipt",
    )
    need(receipt["status"] == "complete", "a complete status with another receipt")
    need(
        receipt["results"]["ref"] == "replay-state"
        and receipt["results"]["path"] == f"requests/{request_id}/results/",
        "the receipt's results are not this request's on replay-state",
    )
    request = json.loads((directory / "REQUEST.json").read_bytes())
    if strict:
        need(
            interface.validate_request(request) == request_id,
            "REQUEST.json is not the request its directory names",
        )
    results = directory / "results"
    variant_path = results / "VARIANT.json"
    need(variant_path.is_file(), "a complete receipt without results/VARIANT.json")
    record_bytes = variant_path.read_bytes()
    record = json.loads(record_bytes)
    need(record_bytes == canonical_bytes(record), "VARIANT.json is not canonical")
    if record.get("status") != "certified":
        raise Ineligible(
            f"{record.get('variant_id')} is {record.get('status')}: "
            "only certified variants are committed to main"
        )
    need(
        record["variant_id"] == receipt["variant_id"]
        and record["identity_sha256"] == receipt["variant_identity_sha256"],
        "VARIANT.json is not the receipt's variant",
    )
    # An exactly certified pair qualified again (a determinism check) returns
    # the committed record, note included: its results are already on main.
    # The id gains its digest suffix only when main already holds the slug,
    # so two runs that finish before either merges can share an id with
    # different identities: the second is refused, to be qualified again.
    need(
        record["identity_sha256"] == variants.identity_sha256(record.get("identity")),
        "VARIANT.json's identity_sha256 is not its identity's digest",
    )
    document = variants.load_document(checkout / INDEX)
    ids = [v["variant_id"] for v in document["variants"]]
    if record["variant_id"] in ids:
        # The same variant is the same id and identity. The committed record
        # is VARIANT.json plus the note the results pull request added, and a
        # later change to the index (a schema migration) may add or reshape
        # its other fields, so they are not compared.
        committed = document["variants"][ids.index(record["variant_id"])]
        need(
            (committed["variant_id"], committed["identity_sha256"])
            == (record["variant_id"], record["identity_sha256"]),
            f"{record['variant_id']} already names another identity in {INDEX}; "
            "qualify this pair again so it gets its own id",
        )
        need(
            committed["status"] == "certified",
            f"{INDEX} holds {record['variant_id']} as {committed['status']}, "
            "not certified",
        )
        raise Ineligible(f"{record['variant_id']} is already in {INDEX}")
    need(record["layout"] == "replay_namespace", "a certified result needs a namespace")
    need("note" not in record, "VARIANT.json already carries a note")
    # The id names a branch, paths and a CI matrix leg.
    need(
        plain_variant_id(record["variant_id"]),
        f"variant_id {record['variant_id']!r} cannot name a branch and paths",
    )
    need(
        record["requirements"]["path"]
        == f"docs/uk_replay/requirements/{record['variant_id']}.txt",
        "VARIANT.json names its freeze somewhere other than docs/uk_replay/requirements/",
    )
    # results/ mirrors the repository, so the record validates against it.
    variants.validate_record(record, root=directory / "results")
    need(
        record.get("qualification_request_sha256") == request_id,
        "VARIANT.json was built from another request",
    )
    # The newest certified variant is the last certified record (append
    # order), which is what a later qualification diffs against.
    previous = qualify.latest_certified(document)
    need(
        version_key(wrapper_version(record)) >= version_key(wrapper_version(previous)),
        f"policyengine {wrapper_version(record)} is older than the newest certified "
        f"{wrapper_version(previous)}; appended, it would become latest_certified",
    )
    paths = result_paths(record, receipt)
    if receipt.get("diff"):
        need(
            receipt["diff"]["base_variant_id"] in ids,
            "the release diff's base is not a committed variant",
        )
    namespace = results / paths["namespace"]
    allowed = [f"{paths['namespace']}/", paths["requirements"]]
    if paths["diff"]:
        allowed.append(f"{paths['diff']}/")
    files = 0
    total = 0
    for path in sorted(results.rglob("*")):
        relative = path.relative_to(results).as_posix()
        need(not path.is_symlink(), f"{relative} is a link")
        if path.is_dir():
            continue
        need(path.is_file(), f"{relative} is not a regular file")
        if relative == "VARIANT.json":
            continue
        need(
            any(
                relative == prefix
                or (prefix.endswith("/") and relative.startswith(prefix))
                for prefix in allowed
            ),
            f"results/{relative} is outside the namespace, its diff and its freeze",
        )
        files += 1
        total += path.stat().st_size
    need(
        (namespace / variants.RECEIPT_NAME).is_file()
        and (namespace / variants.RECEIPT_NAME).read_bytes() == receipt_bytes,
        "the namespace's sealed receipt differs from the request's receipt",
    )
    need(
        (namespace / "NAMESPACE_MANIFEST.json").is_file()
        and sha256_bytes((namespace / "NAMESPACE_MANIFEST.json").read_bytes())
        == receipt["results"]["manifest_sha256"],
        "the namespace manifest is not the one the receipt binds",
    )
    requirements = results / paths["requirements"]
    need(
        requirements.is_file()
        and sha256_bytes(requirements.read_bytes()) == record["requirements"]["sha256"],
        "the requirements freeze is missing or differs from VARIANT.json",
    )
    if paths["diff"]:
        diff_json = results / paths["diff"] / "DIFF.json"
        need(
            diff_json.is_file()
            and sha256_bytes(diff_json.read_bytes()) == receipt["diff"]["diff_sha256"],
            "the release diff is missing or not the one the receipt binds",
        )
    for key in ("namespace", "diff", "requirements"):
        if paths[key]:
            need(
                not (checkout / paths[key]).exists(),
                f"main already holds {paths[key]}",
            )
    history = status["history"]
    return {
        "action": "build",
        "request_id": request_id,
        "variant_id": record["variant_id"],
        "version": wrapper_version(record),
        "branch": f"{BRANCH_PREFIX}{record['variant_id']}",
        "title": f"Certify the policyengine.py {wrapper_version(record)} replay results",
        "draft": receipt["integrity"]["status"] != "complete",
        "previous_newest": previous["variant_id"],
        "previous_last": ids[-1],
        "paths": paths,
        "results_files": files,
        "results_bytes": total,
        "completed_at": completed_at(status),
        "receipt_sha256": receipt["receipt_sha256"],
        "receipt_commit": status["receipt_commit"],
        "state_commit": state_commit,
        "run_url": history[-1]["run_url"],
        "kind": request["kind"],
        "attempt": request.get("attempt"),
        "compare_to": request.get("compare_to", "latest_certified"),
        "legacy_variant": document["default_variant"],
    }


# --- editing --------------------------------------------------------------------


def note(record: dict, plan: dict) -> str:
    bundle = record["identity"]["release_bundle"]
    certified_for = record["certification"]["certified_for_model_version"]
    data = (
        f"data built with policyengine-uk {bundle['data_build_model_version']} "
        f"and certified for {certified_for}"
        if bundle.get("data_build_model_version")
        else f"data certified for policyengine-uk {certified_for}"
    )
    kind = "released bundle" if plan["kind"] == "released_bundle" else plan["kind"]
    return (
        f"The {wrapper_version(record)} {kind}, qualified through the receiver on "
        f"{day(plan['completed_at'])} (request {plan['request_id'][:8]}, receipt "
        f"{plan['receipt_sha256'][:8]}); {data}."
    )


def append_variant(raw: bytes, record: dict, note_text: str) -> bytes:
    """The index with one more record, in canonical form; the rest unchanged."""
    document = json.loads(raw)
    need(raw == canonical_bytes(document), f"{INDEX} on main is not canonical")
    document["variants"].append({**record, "note": note_text})
    return canonical_bytes(document)


def replace_newest(text: str, previous: str, variant_id: str, *, name: str) -> str:
    matches = list(NEWEST.finditer(text))
    need(len(matches) == 1, f"{name} must define NEWEST exactly once")
    need(
        matches[0].group(1) == previous,
        f"{name} names {matches[0].group(1)} as NEWEST, not the newest certified "
        f"{previous}",
    )
    start, end = matches[0].span()
    return f'{text[:start]}NEWEST = "{variant_id}"{text[end:]}'


def append_committed(text: str, previous: str, variant_id: str, *, name: str) -> str:
    matches = list(COMMITTED.finditer(text))
    need(len(matches) == 1, f"{name} must define the COMMITTED tuple exactly once")
    body = matches[0].group(1)
    need(
        body.splitlines()[-1] == f'    "{previous}",',
        f"{name}'s COMMITTED tuple does not end with {previous}",
    )
    end = matches[0].start(1) + len(body)
    return f'{text[:end]}    "{variant_id}",\n{text[end:]}'


def paragraph(record: dict, receipt: dict, plan: dict) -> str:
    """The RELEASE_REPLAY.md paragraph: counts and aggregates from the
    receipt, nothing interpreted."""
    integrity = receipt["integrity"]
    failures = integrity["failures"]
    if failures:
        codes: dict[str, int] = {}
        for failure in failures:
            codes[failure["code"]] = codes.get(failure["code"], 0) + 1
        listed = ", ".join(f"{code} {count}" for code, count in sorted(codes.items()))
        integrity_text = (
            f"Integrity is {integrity['status']} with "
            f"{counted(len(failures), 'failure')} ({listed})"
        )
    else:
        integrity_text = f"Integrity is {integrity['status']} with no failures"
    events = (receipt.get("corpus") or {}).get("events") or {}
    complete = sum(e["full_supported_grid_complete"] for e in events.values())
    inert = sum(len(e["inert_measure_years"]) for e in events.values())
    if not events:
        grids = "; the receipt records no event results."
    elif complete == len(events) and not inert:
        grids = (
            f", and all {counted(len(events), 'event')} have complete supported "
            "grids and no inert measure-years."
            if len(events) > 1
            else ", and its one event has a complete supported grid and no inert "
            "measure-years."
        )
    else:
        grids = (
            f"; {number(complete)} of {counted(len(events), 'event')} "
            f"{'has a complete supported grid' if complete == 1 else 'have complete supported grids'}"
            f", with {counted(inert, 'inert measure-year')} in all."
        )
    diff = receipt.get("diff")
    if diff:
        base = diff["base_variant_id"]
        which = "the legacy variant " if base == plan["legacy_variant"] else ""
        why = (
            ", the newest certified variant with committed results at the time"
            if plan["compare_to"] == "latest_certified"
            else ", the base the request named"
        )
        rows = len(diff["flagged_rows"])
        counts = [
            f"{flag} {n:,}" for flag, n in sorted(diff["flag_counts"].items()) if n
        ]
        if counts:
            listed = (
                counts[0]
                if len(counts) == 1
                else ", ".join(counts[:-1]) + f" and {counts[-1]}"
            )
            flags = (
                f"That diff flags {counted(rows, 'row')}; its flag counts are "
                f"{listed}, and every other flag count is zero."
            )
        else:
            flags = "That diff flags no rows."
        diff_text = f"Its release diff is against {which}`{base}`{why}. {flags}"
    else:
        diff_text = "It has no release diff."
    text = (
        f"`{record['result_root']}/` holds the qualification of policyengine.py "
        f"{wrapper_version(record)}: request `{plan['request_id'][:8]}…`, receipt "
        f"SHA-256 `{plan['receipt_sha256'][:8]}…`, `replay-state` commit "
        f"`{plan['receipt_commit'][:7]}`. {integrity_text}{grids} {diff_text} "
        "The results pull request wrote this paragraph from the receipt's counts."
    )
    return textwrap.fill(text, width=76, break_long_words=False, break_on_hyphens=False)


def insert_paragraph(text: str, addition: str) -> str:
    """Append ``addition`` to the end of the Committed certified results
    subsection, before the next heading."""
    lines = text.split("\n")
    starts = [i for i, line in enumerate(lines) if line == SECTION]
    need(len(starts) == 1, f"{DOC} must have exactly one {SECTION!r} heading")
    end = next(
        (
            i
            for i in range(starts[0] + 1, len(lines))
            if lines[i].startswith("## ") or lines[i].startswith("### ")
        ),
        None,
    )
    need(end is not None, f"{SECTION!r} must be followed by another heading")
    need(lines[end - 1] == "", f"{SECTION!r} must end with a blank line")
    return "\n".join([*lines[:end], *addition.split("\n"), "", *lines[end:]])


def commit_message(plan: dict) -> str:
    diff = plan["paths"]["diff"]
    return (
        f"{plan['title']}\n\n"
        + textwrap.fill(
            f"Commit the receiver's sealed qualification of {plan['variant_id']} "
            f"from replay-state request {plan['request_id']} (receipt "
            f"{plan['receipt_sha256']}, receipt commit {plan['receipt_commit']}): "
            "its results"
            + (" and release diff" if diff else "")
            + " and requirements freeze byte for byte, the variant record (which "
            "adds it to CI's replay-engine matrix), the tests that name the newest "
            "certified variant and a RELEASE_REPLAY.md paragraph from the "
            "receipt's counts.",
            width=72,
            break_long_words=False,
            break_on_hyphens=False,
        )
        + f"\n\n{TRAILER}: {plan['request_id']}\n"
    )


def apply(directory: Path, checkout: Path, plan: dict) -> None:
    """Edits 2 to 4, after the workflow extracted the results into checkout.
    The standard library alone, in both jobs."""
    record = json.loads((directory / "results" / "VARIANT.json").read_bytes())
    receipt = json.loads((directory / variants.RECEIPT_NAME).read_bytes())
    for key in ("namespace", "diff", "requirements"):
        if plan["paths"][key]:
            need(
                (checkout / plan["paths"][key]).exists(),
                f"{plan['paths'][key]} was not extracted",
            )
    index = checkout / INDEX
    index.write_bytes(append_variant(index.read_bytes(), record, note(record, plan)))
    document = variants.load_document(index)
    variants.validate_record(document["variants"][-1], root=checkout)
    for name in NEWEST_TESTS:
        path = checkout / name
        path.write_text(
            replace_newest(
                path.read_text(), plan["previous_newest"], plan["variant_id"], name=name
            )
        )
    path = checkout / COMMITTED_TEST
    path.write_text(
        append_committed(
            path.read_text(),
            plan["previous_last"],
            plan["variant_id"],
            name=COMMITTED_TEST,
        )
    )
    doc = checkout / DOC
    doc.write_text(insert_paragraph(doc.read_text(), paragraph(record, receipt, plan)))


def scope(plan: dict, changed: list[str]) -> None:
    """The commit touches the extracted results and the four edits, nothing
    else, and never anything under ``.github/``: the token that pushes it has
    no ``workflows`` permission, and nothing here edits what a workflow runs."""
    workflow_paths = [path for path in changed if path.startswith(UNTOUCHED)]
    need(
        not workflow_paths,
        f"the commit touches {UNTOUCHED}, which a results commit never does: "
        f"{workflow_paths[:10]}",
    )
    paths = plan["paths"]
    trees = [f"{paths['namespace']}/"] + (
        [f"{paths['diff']}/"] if paths["diff"] else []
    )
    outside = [
        path
        for path in changed
        if path not in EDITED
        and path != paths["requirements"]
        and not any(path.startswith(tree) for tree in trees)
    ]
    need(not outside, f"the commit touches more than the results: {outside[:10]}")
    missing = sorted(set(EDITED) - set(changed))
    need(not missing, f"the commit lacks edits to {missing}")


# --- CI's own checks on the commit ------------------------------------------------

# The build job runs ci.yml's format check and suite on the results commit,
# then its no-drift check (review of 24434729, 3). Each is reported as its
# exit status (drift's is 1 when the tree is not clean), how many distinct
# things failed and the first LISTED of them the pull request can show. A
# failure opens the pull request as a draft that names them, where #195, #204
# and #206 opened ready and failed CI.
PREFLIGHT = {
    "ruff": (
        "CI's format check, `uvx ruff format --check be nz scorecard_db tests pipeline`",
        "file",
    ),
    "suite": (
        "CI's suite, `pytest tests/ -q` with CI's packages",
        "failed or erroring test",
    ),
    "drift": (
        "CI's no-drift check after the suite, `git status --porcelain`",
        "changed or untracked path",
    ),
}
# At most LISTED names of at most 200 characters per check: three full
# lists (about 31,000 characters) leave the rest of the body well inside
# GitHub's 65,536-character limit, and the job output inside its 1 MB.
LISTED = 50
# A name the pull request shows sits in a fenced block: printable ASCII, no
# backtick (which could close the fence), no space at either end.
LISTABLE = re.compile(r"[!-_a-~](?:[ -_a-~]{0,198}[!-_a-~])?")
SUMMARY = re.compile(r"^=+ short test summary info =+$", re.M)
# ruff format --check names a file "Would reformat: PATH" before ruff 0.16
# and in a diagnostic's "--> PATH:LINE:COLUMN" after it; CI's uvx ruff is
# whichever is newest.
UNFORMATTED = re.compile(r"^(?:Would reformat: (.+)|\s*--> (.+?):[0-9]+:[0-9]+)$", re.M)


# A node id: a path and names, which hold no space or "[", then, when it is
# parametrised, its brackets up to the first "]" its " - " message (or the
# line's end) follows. A parameter may hold " - " or an unmatched "[".
NODE_ID = re.compile(r"[^\s\[]+(?:\[.*?\])?(?= - |$)")


def node_id(text: str) -> str:
    """A short-summary line's node id, less its " - " message."""
    match = NODE_ID.match(text)
    return match.group() if match else text.split(" - ", 1)[0]


def suite_failures(log: str) -> list[str]:
    """The node ids pytest's last short test summary in ``log`` names as
    FAILED or ERROR (a collection error names its module). On CI pytest
    prints whole messages, over lines. This reads a message line that
    itself starts with FAILED or ERROR as another id, and one that is
    itself a summary header drops the ids before it. Only the list changes:
    a check's exit status, not this list, says whether it failed."""
    starts = [match.end() for match in SUMMARY.finditer(log)]
    if not starts:
        return []
    return [
        node_id(line.split(" ", 1)[1])
        for line in log[starts[-1] :].splitlines()
        if line.startswith(("FAILED ", "ERROR "))
    ]


def format_failures(log: str) -> list[str]:
    """The files ``ruff format --check`` names in ``log``."""
    return [old or new for old, new in UNFORMATTED.findall(log)]


def drift_paths(porcelain: str) -> list[str]:
    """The paths ``git status --porcelain`` lists, changed or untracked."""
    return [line[3:] for line in porcelain.splitlines() if line.strip()]


def report(status: int, names: list[str]) -> dict:
    """One check: its exit status and, when it failed, how many distinct
    names it gave and the first LISTED of those the pull request can show."""
    distinct = list(dict.fromkeys(names)) if status else []
    return {
        "exit": status,
        "count": len(distinct),
        "names": [name for name in distinct if LISTABLE.fullmatch(name)][:LISTED],
    }


def preflight(
    ruff_exit: int, ruff_log: str, suite_exit: int, suite_log: str, porcelain: str
) -> dict:
    """The build job's report of CI's checks on the results commit."""
    return {
        "ruff": report(ruff_exit, format_failures(ruff_log)),
        "suite": report(suite_exit, suite_failures(suite_log)),
        "drift": report(1 if porcelain.strip() else 0, drift_paths(porcelain)),
    }


def read_preflight(text: str) -> dict:
    """The build job's report as the propose job receives it, a string:
    refused unless it has exactly the shape ``preflight`` gives. The
    counts and names are still the build job's word; CI on the pull request
    runs the checks again. A count stays under a billion, because the body
    prints it: a run that names more distinct failures stops here, with
    nothing proposed."""
    try:
        value = json.loads(text)
    except ValueError:
        value = None

    def shaped(condition: bool, what: str) -> None:
        need(condition, f"the build job's outputs are malformed: preflight {what}")

    shaped(isinstance(value, dict) and set(value) == set(PREFLIGHT), "checks")
    for key, check in value.items():
        shaped(
            isinstance(check, dict) and set(check) == {"exit", "count", "names"},
            f"{key} fields",
        )
        status, count, names = check["exit"], check["count"], check["names"]
        shaped(type(status) is int and 0 <= status <= 255, f"{key} exit")
        shaped(type(count) is int and 0 <= count < 10**9, f"{key} count")
        shaped(status != 0 or count == 0, f"{key} passes with failures")
        shaped(
            isinstance(names, list)
            and len(names) <= min(count, LISTED)
            and all(isinstance(n, str) and LISTABLE.fullmatch(n) for n in names)
            and len(set(names)) == len(names),
            f"{key} names",
        )
    return value


def failed_checks(checks: dict) -> list[str]:
    return [key for key in PREFLIGHT if checks[key]["exit"]]


def is_draft(plan: dict, checks: dict) -> bool:
    """A draft when integrity is not complete or any of CI's checks fails."""
    return bool(plan["draft"] or failed_checks(checks))


def check_line(key: str, check: dict) -> str:
    """The check's line under "Validation in the results run": what failed,
    in a fenced block."""
    what, noun = PREFLIGHT[key]
    if not check["exit"]:
        return f"- {what}: passes."
    line = f"- {what}: **fails**" + (
        f" (exit {check['exit']})" if key != "drift" else ""
    )
    count, names = check["count"], check["names"]
    if not count:
        return f"{line}, naming no {noun}; the build job's log has its output."
    line += f", {tally(count, noun)}:"
    if not names:
        return f"{line} none can be shown here; the build job's log lists them."
    listing = "\n".join(f"  {name}" for name in names)
    more = count - len(names)
    rest = f"\n\n  {more:,} more are in the build job's log." if more else ""
    return f"{line}\n\n  ```text\n{listing}\n  ```{rest}"


# --- the pull request -----------------------------------------------------------


def body(directory: Path, plan: dict, validation: dict) -> str:
    reported = read_preflight(validation["preflight"])
    record = json.loads((directory / "results" / "VARIANT.json").read_bytes())
    receipt = json.loads((directory / variants.RECEIPT_NAME).read_bytes())
    packages = record["identity"]["packages"]
    dataset = record["identity"]["dataset"]
    bundle = record["identity"]["release_bundle"]
    integrity = receipt["integrity"]
    events = (receipt.get("corpus") or {}).get("events") or {}
    complete = sum(e["full_supported_grid_complete"] for e in events.values())
    inert = sum(len(e["inert_measure_years"]) for e in events.values())
    diff = receipt.get("diff")
    paths = plan["paths"]
    rows = [
        (
            "Request",
            f"`{plan['request_id']}` ({plan['kind']}"
            + (f", attempt {plan['attempt']}" if plan.get("attempt") else "")
            + ")",
        ),
        (
            "Receipt",
            f"SHA-256 `{plan['receipt_sha256']}`, `replay-state` commit "
            f"`{plan['receipt_commit'][:7]}`",
        ),
        ("Run", plan["run_url"]),
        (
            "Engine",
            f"policyengine.py {packages['policyengine']['version']}, policyengine-uk "
            f"{packages['policyengine-uk']['version']}, core "
            f"{packages['policyengine-core']['version']}",
        ),
        (
            "Data",
            f"{bundle['certified_data_build_id']}, `{dataset['path']}` "
            f"(`{dataset['sha256'][:8]}…{dataset['sha256'][-4:]}`)",
        ),
        (
            "Integrity",
            f"{integrity['status']}, {tally(len(integrity['failures']), 'failure')}; "
            f"complete supported grids for {complete} of {tally(len(events), 'event')}, "
            f"{tally(inert, 'inert measure-year')}",
        ),
    ]
    if diff:
        counts = ", ".join(
            f"{flag} {n:,}" for flag, n in sorted(diff["flag_counts"].items())
        )
        rows.append(
            (
                f"Diff vs `{diff['base_variant_id']}`",
                f"{counts}; {tally(len(diff['flagged_rows']), 'flagged row')}",
            )
        )
    table = "\n".join(f"| {key} | {value} |" for key, value in rows)
    changes = [
        f"- `{paths['namespace']}/`"
        + (f" and `{paths['diff']}/`" if paths["diff"] else "")
        + f": the receiver's `requests/{plan['request_id'][:8]}…/results/` tree, "
        f"byte for byte: {plan['results_files']:,} files, "
        f"{plan['results_bytes'] / 1e6:.1f} MB of aggregate outputs"
        + (" and release-diff packets" if paths["diff"] else "")
        + ".",
        f"- `{paths['requirements']}`: the variant's requirements freeze.",
        f"- `{INDEX}`: the variant record, the qualification's `VARIANT.json` "
        "exactly plus a `note`, in canonical form. CI's replay-engine matrix "
        "lists the index's certified variants, so it replays this one too; no "
        "workflow changes.",
        f"- `{NEWEST_TESTS[0]}` and `{NEWEST_TESTS[1]}` (`NEWEST`) and "
        f"`{COMMITTED_TEST}` (`COMMITTED`): the tests that name the newest "
        "certified variant move to it.",
        f'- `{DOC}`: a "Committed certified results" paragraph from the '
        "receipt's counts.",
    ]
    checks = [
        "- The receiver's output guard, applied again to the request's tree: "
        "every file an allowed, parsable aggregate.",
        f"- Byte identity: all {tally(validation['identical_files'], 'committed result file')} "
        "have the blob replay-state holds; the receipt and results are unchanged "
        "since the receipt commit.",
        f"- `uk_replay_qualify verify-sealed`: {validation['verify_sealed']}.",
        "- CI's `.github/scripts/uk_replay_regenerate.sh` leaves the tree unchanged.",
        "- `scorecard_db.build_db`: two builds agree "
        f"(`{validation['content_hash'][:8]}…`), and there is no tracked-file drift.",
        *(check_line(key, reported[key]) for key in PREFLIGHT),
    ]
    draft = (
        "\n\nIntegrity is not `complete`, so this pull request is a draft: decide "
        "whether this run should become the committed base before marking it ready."
        if plan["draft"]
        else ""
    )
    if failed_checks(reported):
        draft += (
            "\n\nCI's own checks fail on this commit (see \"Validation in the "
            'results run"), so this pull request is a draft. Fix them on main and '
            "run the results workflow again for this request, which rebuilds this "
            "branch on the new main; mark the pull request ready once CI passes."
        )
    return (
        f"# {plan['title']}\n\n"
        f"This PR commits the receiver's sealed qualification of `{plan['variant_id']}`"
        + (
            f", with its release diff against `{diff['base_variant_id']}`"
            if diff
            else ""
        )
        + ". The results workflow (`.github/workflows/uk-replay-results.yml`) built it "
        "from the committed receipt, as #188 and #190 were built by hand. Merging "
        "stays on the normal gates: CI and an independent review."
        f"{draft}\n\n| | |\n|---|---|\n{table}\n\n## What changes\n\n"
        + "\n".join(changes)
        + "\n\n## Validation in the results run\n\n"
        + "\n".join(checks)
        + "\n\nThe table and the RELEASE_REPLAY.md paragraph state counts only. "
        "Reviewers add any interpretation of flagged rows.\n\n"
        f"{AXIOM}\n"
    )


# --- the command line -----------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "apply", "body"):
        sub = commands.add_parser(name)
        sub.add_argument("--request-dir", type=Path, required=True)
        sub.add_argument("--plan", type=Path, required=True)
        if name != "body":
            sub.add_argument("--checkout", type=Path, required=True)
        if name == "check":
            sub.add_argument("--request-id", required=True)
            sub.add_argument("--state-commit", required=True)
        if name == "apply":
            sub.add_argument("--commit-message", type=Path, required=True)
        if name == "check":
            # The propose job: standard library only (python3 -I -S).
            sub.add_argument("--stdlib", action="store_true")
        if name == "body":
            sub.add_argument("--validation", type=Path, required=True)
            sub.add_argument("--output", type=Path, required=True)
    scoped = commands.add_parser("scope")
    scoped.add_argument("--plan", type=Path, required=True)
    # The build job's report of CI's checks, one line of JSON for job 2.
    reported = commands.add_parser("preflight")
    for name in ("ruff", "suite"):
        reported.add_argument(f"--{name}-exit", type=int, required=True)
        reported.add_argument(f"--{name}-log", type=Path, required=True)
    reported.add_argument("--porcelain", type=Path, required=True)
    reported.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "check":
            try:
                plan = check(
                    args.request_dir,
                    args.checkout,
                    args.request_id,
                    args.state_commit,
                    strict=not args.stdlib,
                )
            except Ineligible as reason:
                plan = {"action": "skip", "reason": str(reason)}
            args.plan.write_bytes(canonical_bytes(plan))
            print(plan["action"], plan.get("reason", plan.get("variant_id")))
        elif args.command == "apply":
            plan = json.loads(args.plan.read_bytes())
            apply(args.request_dir, args.checkout, plan)
            args.commit_message.write_text(commit_message(plan))
        elif args.command == "scope":
            plan = json.loads(args.plan.read_bytes())
            scope(plan, [line for line in sys.stdin.read().splitlines() if line])
        elif args.command == "preflight":
            text = json.dumps(
                preflight(
                    args.ruff_exit,
                    args.ruff_log.read_text(errors="replace"),
                    args.suite_exit,
                    args.suite_log.read_text(errors="replace"),
                    args.porcelain.read_text(errors="replace"),
                ),
                separators=(",", ":"),
                sort_keys=True,
            )
            # Never a report job 2 would refuse.
            read_preflight(text)
            args.output.write_text(text)
        else:
            plan = json.loads(args.plan.read_bytes())
            validation = json.loads(args.validation.read_bytes())
            args.output.write_text(body(args.request_dir, plan, validation))
            # The propose job opens a draft on this word.
            print(
                "true"
                if is_draft(plan, read_preflight(validation["preflight"]))
                else "false"
            )
    except (Refused, variants.VariantError) as problem:
        print(f"::error::{problem}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
