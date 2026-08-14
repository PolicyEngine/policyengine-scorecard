"""Registry-consistency tests for the UK compute pipeline (#40).

The pipeline itself needs the policyengine.py-managed environment and
the certified populace-uk bundle; these tests pin what is checkable
anywhere — the declarative registries are internally consistent and the
module imports without the engine installed.
"""

from pipeline.compute_uk_counterparts import (
    BENEFIT_LINES,
    CANDIDATES,
    FULLPART_OVERRIDES,
    emit,
    meta,
    pe_gap,
    rows,
)


def test_module_imports_without_engine():
    # the policyengine import lives inside build_sim(), so the registry
    # is inspectable (and testable) on unmanaged machines
    assert CANDIDATES and BENEFIT_LINES and FULLPART_OVERRIDES


def test_benefit_lines_reference_known_concepts():
    for program, concept, entity, geo in BENEFIT_LINES:
        assert concept in CANDIDATES, f"{program}: unknown concept {concept}"
        assert entity in ("person", "benunit", "household")
        assert geo in ("UK", "GB", "NI")


def test_candidate_lists_are_nonempty_and_unique():
    for concept, names in CANDIDATES.items():
        assert names, f"{concept}: empty candidate list"
        assert len(names) == len(set(names)), f"{concept}: duplicate candidates"


def test_emit_and_pe_gap_row_shape():
    before = len(rows)
    emit("baseline", "pension_credit", "recipient_count", "total", "GB", 1_320_000)
    pe_gap("baseline", "x", "m", "total", "UK", "some_concept")
    ok_row, gap_row = rows[before], rows[before + 1]
    assert ok_row["country"] == "UK" and ok_row["status"] == "ok"
    assert ok_row["value"] == 1_320_000.0
    assert gap_row["status"] == "pe_gap" and gap_row["value"] is None
    assert meta["unresolved"][-1]["concept"] == "some_concept"
    del rows[before:]
    meta["unresolved"].pop()
