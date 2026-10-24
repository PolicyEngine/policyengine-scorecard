"""Export certified UK fiscal-event replays for the Autumn Budget dashboard.

The dashboard (PolicyEngine/uk-autumn-budget-dashboard-2026) can show past
fiscal events next to the current Budget. It runs its own pipeline on its own
model and data pair, so what it takes from a replay is the construction, not
the numbers: for each computed measure, the baseline and reform parameter
dictionaries the replay submitted to the engine, its declared fiscal heads,
and, for the differential check, the replay's per-year totals on the replay's
pair. For every measure, computed or not, it takes the registry's
classification and reason, and the OBR side of each source row. The event's
source-inventory accounting is the registry's, recomputed here and required
to agree exactly.

Everything read is bound to the sealed namespace: the variant's
REPLAY_RECEIPT.json names NAMESPACE_MANIFEST.json's digest, which lists the
digest of every file the export reads there, and each event's RUN_MANIFEST.json
names the registry digest the replay ran. A file that does not match is
refused; nothing is exported from it.

No household-level value is read or written: artifacts carry national
aggregates only, and the OBR rows are published costings.

    PYTHONPATH=. python pipeline/export_uk_events_dashboard.py \
        [--variant <variant_id>] [--events <slug> ...] [--output-root <dir>]

Without --variant the newest certified replay-namespace variant is used. The
output is results/uk/dashboard_export/<variant_id>/<event>.json and an
EXPORT_MANIFEST.json listing each file's digest. Bytes depend only on the
committed inputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from collections import defaultdict
from contextlib import contextmanager
from decimal import Decimal, Inexact, localcontext
from fractions import Fraction
from pathlib import Path

from pipeline import compute_uk_ab2025 as worlds
from pipeline import compute_uk_event as replay
from pipeline import uk_replay_variants as variants

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "policyengine-scorecard/uk-event-dashboard-export/v1"
EXPORT_ROOT = ROOT / "results" / "uk" / "dashboard_export"
EXPORT_MANIFEST = "EXPORT_MANIFEST.json"
CLASSES = ("expressible", "partial", "not_expressible", "out_of_household_scope")
COMPUTABLE = ("expressible", "partial")
GAP_KINDS = ("construction_pending", "model_or_data_gap")
CONSTRUCTED = "constructed"
# Constructions whose replay route is more than a parameter dictionary: the
# replay refreshes Universal Credit's seeded cohort after the parameter change
# (compute_uk_event.uc_health_scenario). An importer must reproduce the route,
# not just the dictionary.
EXECUTOR_ROUTES = {replay.UC_HEALTH_ELEMENT_PARAMETER: "uc_health_element_refresh"}

SEMANTICS = (
    "Each computed measure is costed on the replay's certified model and data, "
    "holding the rest of the law at what that engine treats as current law. A "
    "reversal_on_certified_world measure is in current law: its baseline world "
    "undoes it (baseline_world.submitted_reform) and its reform world is "
    "current law. A forward_delta_on_certified_world measure is not in current "
    "law: its baseline world is current law and its reform world adds it "
    "(reform_world.submitted_reform). measure_total_gbp is the sum of the "
    "declared fiscal heads' Exchequer effects, positive meaning a gain to the "
    "Exchequer; replay year Y is calendar year Y, the proxy for fiscal year "
    "Y-(Y+1). These are not the estimates made at the time of the event."
)


class ExportError(ValueError):
    """An input does not match what the sealed namespace says it is."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode()


@contextmanager
def exact():
    """Decimal arithmetic that refuses to round.

    The registry's sums of 1,000-odd cells run past the default 28 digits; a
    sum that would round raises instead of disagreeing silently."""
    with localcontext() as context:
        context.prec = 1000
        context.traps[Inexact] = True
        yield


def decimal_text(value: Decimal) -> str:
    """Exact decimal text, with no exponent and no trailing zeros."""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def share_text(part: Decimal, whole: Decimal) -> str | None:
    """part/whole as an exact fraction "p/q" (None when whole is zero).

    Shares are exact, so the shares of a partition sum to exactly one."""
    if whole == 0:
        return None
    fraction = Fraction(part) / Fraction(whole)
    return f"{fraction.numerator}/{fraction.denominator}"


class Namespace:
    """The sealed files of one certified variant, each read once and checked."""

    def __init__(self, record: dict, *, root: Path = ROOT):
        if record.get("status") != "certified":
            raise ExportError(f"{record['variant_id']} is not certified")
        if variants.is_legacy(record):
            raise ExportError(
                f"{record['variant_id']} is the legacy namespace: export a "
                "replay_namespace variant, which records processed parameters"
            )
        try:
            variants.validate_record(record, root=root)
        except variants.VariantError as exc:
            raise ExportError(f"invalid variant record: {exc}") from exc
        identity_sha256 = variants.identity_sha256(record["identity"])
        self.root = root
        self.record = record
        self.path = variants.namespace_root(record, root=root)
        receipt_bytes = (self.path / variants.RECEIPT_NAME).read_bytes()
        receipt = json.loads(receipt_bytes)
        if (
            receipt.get("status") != "complete"
            or receipt.get("integrity", {}).get("status") != "complete"
            or receipt.get("variant_id") != record["variant_id"]
        ):
            raise ExportError(
                f"{self.path}: receipt is not a complete seal of this variant"
            )
        if receipt.get("variant_identity_sha256") != identity_sha256:
            raise ExportError(
                f"{self.path}: receipt names a different variant identity"
            )
        manifest_bytes = (self.path / "NAMESPACE_MANIFEST.json").read_bytes()
        if sha256_bytes(manifest_bytes) != receipt["results"]["manifest_sha256"]:
            raise ExportError(
                f"{self.path}: NAMESPACE_MANIFEST.json is not the sealed one"
            )
        self.receipt = receipt
        self.receipt_sha256 = sha256_bytes(receipt_bytes)
        self.manifest_sha256 = sha256_bytes(manifest_bytes)
        self.files = json.loads(manifest_bytes)["files"]

    def read(self, relative: str) -> bytes:
        """A namespace file's bytes, refused unless the seal lists that digest."""
        if relative not in self.files:
            raise ExportError(f"{relative} is not listed in the sealed namespace")
        try:
            data = (self.path / relative).read_bytes()
        except FileNotFoundError as exc:
            raise ExportError(f"{relative}: sealed file is missing") from exc
        if sha256_bytes(data) != self.files[relative]:
            raise ExportError(f"{relative} does not match its sealed digest")
        return data

    def json(self, relative: str) -> dict:
        return json.loads(self.read(relative))

    def events(self) -> list[str]:
        events = json.loads(self.read(variants.CORPUS_NAME))["events"]
        manifested = {
            path.removesuffix("/RUN_MANIFEST.json")
            for path in self.files
            if path.endswith("/RUN_MANIFEST.json")
        }
        if len(events) != len(set(events)) or set(events) != manifested:
            raise ExportError("sealed corpus and namespace event inventory disagree")
        return events


def default_variant(document: dict) -> dict:
    """The newest certified replay namespace: the last one the index records."""
    certified = [
        v
        for v in document["variants"]
        if v["status"] == "certified" and not variants.is_legacy(v)
    ]
    if not certified:
        raise ExportError("no certified replay-namespace variant is recorded")
    return certified[-1]


def union_reforms(per_year: list[dict | None], context: str) -> dict | None:
    """One dictionary from each year's submitted reform.

    The replay submits the same construction every year; a construction
    revision can only add windows. Two years submitting different values for
    the same path and window is refused."""
    merged: dict = {}
    seen = False
    for reform in per_year:
        if reform is None:
            continue
        seen = True
        for path, windows in reform.items():
            target = merged.setdefault(path, {})
            for window, value in windows.items():
                if window in target and target[window] != value:
                    raise ExportError(f"{context}: years disagree on {path} {window}")
                target[window] = value
    if not seen:
        return None
    return {
        path: dict(sorted(windows.items())) for path, windows in sorted(merged.items())
    }


def executor_route(*reforms: dict | None) -> str | None:
    routes = {
        route
        for reform in reforms
        for path, route in EXECUTOR_ROUTES.items()
        if reform and path in reform
    }
    if len(routes) > 1:
        raise ExportError(
            f"a construction needs more than one executor route: {sorted(routes)}"
        )
    return routes.pop() if routes else None


def comparison_rows(namespace: Namespace, event: str) -> dict[str, dict]:
    """COMPARISON.csv's rows by source row id (the OBR side and status)."""
    text = namespace.read(f"{event}/COMPARISON.csv").decode()
    rows = {}
    for row in csv.DictReader(io.StringIO(text)):
        if row["source_row_id"] in rows:
            raise ExportError(f"{event}: COMPARISON.csv repeats {row['source_row_id']}")
        rows[row["source_row_id"]] = row
    return rows


def optional_number(text: str) -> float | None:
    return float(text) if text != "" else None


def measure_reason(measure: dict) -> str | None:
    """Why a measure, or part of it, has no PolicyEngine counterpart."""
    classification = measure.get("classification", measure.get("computability"))
    legs = [leg for leg in measure.get("missing_legs") or [] if leg]
    if classification == "out_of_household_scope":
        reasons = sorted(
            {
                row.get("classification_reason")
                for row in measure["source_rows"]
                if row.get("classification") == "out_of_household_scope"
                and row.get("classification_reason")
            }
        )
        legs = legs or reasons
    return " ".join(legs) or measure.get("pe_gap") or None


def accounting(registry: dict) -> dict:
    """The registry's source-inventory accounting, recomputed from its rows.

    Classes partition the source rows; measure counts classify each measure
    once. Both are required to equal the registry's recorded accounting."""
    with exact():
        return _accounting(registry)


def _accounting(registry: dict) -> dict:
    by_class = {
        c: {"measures": 0, "rows": 0, "net": Decimal(0), "absolute": Decimal(0)}
        for c in CLASSES
    }
    gaps = {
        k: {"measures": 0, "rows": 0, "net": Decimal(0), "absolute": Decimal(0)}
        for k in GAP_KINDS
    }
    by_fy = {}
    for measure in registry["measures"]:
        classification = measure.get("classification", measure.get("computability"))
        by_class[classification]["measures"] += 1
        if classification == "not_expressible":
            gaps[measure.get("gap_kind")]["measures"] += 1
        for row in measure["source_rows"]:
            row_class = row.get("classification", classification)
            value = Decimal(row["value_gbp_decimal"])
            fiscal_year = by_fy.setdefault(
                row["fy"], {"rows": 0, "net": Decimal(0), "absolute": Decimal(0)}
            )
            for account in [by_class[row_class], fiscal_year] + (
                [gaps[row.get("gap_kind", measure.get("gap_kind"))]]
                if row_class == "not_expressible"
                else []
            ):
                account["rows"] += 1
                account["net"] += value
                account["absolute"] += abs(value)
    recorded = registry["accounting"]
    for c in CLASSES:
        theirs = recorded["by_class"][c]
        ours = by_class[c]
        if (
            ours["rows"] != theirs["rows"]
            or ours["net"] != Decimal(theirs["net_gbp_decimal"])
            or ours["absolute"] != Decimal(theirs["absolute_gbp_decimal"])
            or ("measures" in theirs and ours["measures"] != theirs["measures"])
        ):
            raise ExportError(
                f"{registry['event_slug']}: {c} accounting differs from the registry"
            )
    total_rows = sum(a["rows"] for a in by_class.values())
    total_net = sum((a["net"] for a in by_class.values()), Decimal(0))
    total_absolute = sum((a["absolute"] for a in by_class.values()), Decimal(0))

    def totals_match(account: dict, rows: int, net: Decimal, absolute: Decimal) -> bool:
        return all(
            account[f"rows_{side}"] == rows
            and Decimal(account[f"net_gbp_{side}_decimal"]) == net
            and Decimal(account[f"absolute_gbp_{side}_decimal"]) == absolute
            for side in ("in", "classified")
        )

    if not totals_match(recorded, total_rows, total_net, total_absolute):
        raise ExportError(
            f"{registry['event_slug']}: accounting totals differ from the registry"
        )
    if set(by_fy) != set(recorded["by_fy"]) or any(
        not totals_match(
            recorded["by_fy"][fy], account["rows"], account["net"], account["absolute"]
        )
        for fy, account in by_fy.items()
    ):
        raise ExportError(
            f"{registry['event_slug']}: fiscal-year accounting differs from the registry"
        )

    def render(account: dict) -> dict:
        return {
            "measures": account["measures"],
            "rows": account["rows"],
            "net_gbp_decimal": decimal_text(account["net"]),
            "absolute_gbp_decimal": decimal_text(account["absolute"]),
            "share_of_absolute": share_text(account["absolute"], total_absolute),
            "share_of_measures": share_text(
                Decimal(account["measures"]), Decimal(len(registry["measures"]))
            ),
        }

    return {
        "amount_basis": recorded["amount_basis"],
        "sign_convention": recorded["sign_convention"],
        "by_class": {c: render(by_class[c]) for c in CLASSES},
        "not_expressible_by_gap_kind": {k: render(gaps[k]) for k in GAP_KINDS},
        "totals": {
            "measures": len(registry["measures"]),
            "rows": total_rows,
            "net_gbp_decimal": decimal_text(total_net),
            "absolute_gbp_decimal": decimal_text(total_absolute),
        },
    }


def computed_accounting(measures: list[dict], totals: dict) -> dict:
    """The source rows with a computed PolicyEngine counterpart, against all."""
    with exact():
        return _computed_accounting(measures, totals)


def _computed_accounting(measures: list[dict], totals: dict) -> dict:
    rows = [row for m in measures for row in m["obr_rows"]]
    absolute = sum(
        (
            abs(Decimal(r["obr_value_gbp_decimal"]))
            for r in rows
            if r["status"] == CONSTRUCTED
        ),
        Decimal(0),
    )
    whole = Decimal(totals["absolute_gbp_decimal"])
    by_status: dict[str, dict] = {}
    for row in rows:
        account = by_status.setdefault(
            row["status"], {"rows": 0, "absolute": Decimal(0)}
        )
        account["rows"] += 1
        account["absolute"] += abs(Decimal(row["obr_value_gbp_decimal"]))
    return {
        "by_status": {
            status: {
                "rows": account["rows"],
                "absolute_gbp_decimal": decimal_text(account["absolute"]),
                "share_of_absolute": share_text(account["absolute"], whole),
            }
            for status, account in sorted(by_status.items())
        },
        "measures": sum(m["computed"] for m in measures),
        "rows": sum(r["status"] == CONSTRUCTED for r in rows),
        "absolute_gbp_decimal": decimal_text(absolute),
        "share_of_absolute": share_text(absolute, whole),
        "share_of_measures": share_text(
            Decimal(sum(m["computed"] for m in measures)), Decimal(totals["measures"])
        ),
    }


def build_event_export(namespace: Namespace, event: str) -> dict:
    """One event's export document."""
    run = namespace.json(f"{event}/RUN_MANIFEST.json")
    provenance = namespace.json(f"{event}/COMPARISON_PROVENANCE.json")
    registry_path = namespace.root / run["registry_path"]
    registry_bytes = registry_path.read_bytes()
    registry_sha256 = sha256_bytes(registry_bytes)
    if (
        registry_sha256 != run["registry_sha256"]
        or registry_sha256 != provenance["registry_sha256"]
    ):
        raise ExportError(
            f"{event}: {run['registry_path']} is not the registry this replay ran"
        )
    registry = json.loads(registry_bytes)
    if registry["event_slug"] != event or run["event"] != event:
        raise ExportError(f"{event}: registry and run name different events")
    if (
        run.get("variant_id", namespace.record["variant_id"])
        != namespace.record["variant_id"]
    ):
        raise ExportError(f"{event}: run belongs to another variant")
    if (
        run["variant_identity_sha256"] != namespace.record["identity_sha256"]
        or run["data_years"] != namespace.record["data_years"]
    ):
        raise ExportError(
            f"{event}: run identity or data years differ from the variant"
        )
    supported, unsupported = variants.supported_years(
        namespace.record, registry["calendar_years"]
    )
    if run["supported_years"] != supported or run["unsupported_years"] != unsupported:
        raise ExportError(f"{event}: run does not cover the registry's supported years")
    index = {m["measure_key"]: m for m in registry["measures"]}
    planned = worlds.computable(index, years=run["supported_years"])
    idle = worlds.not_computable(index, years=run["supported_years"])
    revisions = run.get("construction_revisions") or {}
    rows_by_id = comparison_rows(namespace, event)
    seen_rows: set[str] = set()

    artifacts_by_measure: dict[str, list[dict]] = defaultdict(list)
    artifact_pairs: set[tuple[str, int]] = set()
    prefix = f"{namespace.path.relative_to(namespace.root).as_posix()}/"
    for path, digest in run["artifacts"].items():
        relative = path.removeprefix(prefix)
        if namespace.files.get(relative) != digest:
            raise ExportError(
                f"{event}: {relative} is not sealed with the run's digest"
            )
        artifact = namespace.json(relative)
        if (
            artifact["event"] != event
            or artifact.get("variant_id") != namespace.record["variant_id"]
        ):
            raise ExportError(f"{relative}: artifact names another event or variant")
        pair = (artifact["measure_key"], artifact["year"])
        if pair in artifact_pairs:
            raise ExportError(f"{event}: duplicate artifact measure/year {pair}")
        artifact_pairs.add(pair)
        artifacts_by_measure[artifact["measure_key"]].append(
            {"path": path, "sha256": digest, "artifact": artifact}
        )
    expected_pairs = {
        (key, year)
        for key in planned
        if index[key].get("classification", index[key].get("computability"))
        in COMPUTABLE
        for year in supported
    }
    if artifact_pairs != expected_pairs:
        raise ExportError(
            f"{event}: artifacts do not equal the expected supported-year grid"
        )

    measures = []
    for key in sorted(index):
        measure = index[key]
        classification = measure.get("classification", measure.get("computability"))
        if classification not in CLASSES:
            raise ExportError(f"{key}: unknown classification {classification!r}")
        obr_rows = []
        for source in measure["source_rows"]:
            row = rows_by_id.get(source["source_row_id"])
            if row is None or row["measure_key"] != key:
                raise ExportError(
                    f"{key}: source row {source['source_row_id']} is not in COMPARISON.csv"
                )
            if Decimal(row["obr_value_gbp_decimal"]) != Decimal(
                source["value_gbp_decimal"]
            ):
                raise ExportError(
                    f"{key}: COMPARISON.csv changes the OBR value of {source['source_row_id']}"
                )
            seen_rows.add(source["source_row_id"])
            obr_rows.append(
                {
                    "source_row_id": source["source_row_id"],
                    "fy": source["fy"],
                    "year": int(row["year"]),
                    "tax_head": source["tax_head"],
                    "obr_value_gbp_decimal": decimal_text(
                        Decimal(source["value_gbp_decimal"])
                    ),
                    "classification": source.get("classification", classification),
                    "status": row["status"],
                    "reason": row["reason"] or None,
                    # The replay's own counterpart on the replay's pair, from
                    # COMPARISON.csv: not the dashboard's figure.
                    "replay_pe_value_gbp": optional_number(row["pe_value_gbp"]),
                    "replay_gap_gbp": optional_number(row["gap_gbp"]),
                    "replay_pe_to_obr_ratio": optional_number(row["pe_to_obr_ratio"]),
                    "ratio_bin": row["ratio_bin"],
                }
            )
        obr_rows.sort(key=lambda r: (r["fy"], r["tax_head"], r["source_row_id"]))
        entry = {
            "measure_key": key,
            "title": measure["title"],
            "measure_type": measure.get("measure_type"),
            "classification": classification,
            "gap_kind": measure.get("gap_kind")
            if classification == "not_expressible"
            else None,
            "reason": measure_reason(measure),
            "missing_legs": [leg for leg in measure.get("missing_legs") or [] if leg],
            "construction_note": next(
                (
                    rows_by_id[r["source_row_id"]]["construction_note"]
                    for r in obr_rows
                    if rows_by_id[r["source_row_id"]]["construction_note"]
                ),
                None,
            ),
            "obr_rows": obr_rows,
            "computed": False,
            "construction": None,
            "years": [],
        }
        found = sorted(
            artifacts_by_measure.pop(key, []), key=lambda a: a["artifact"]["year"]
        )
        if classification in COMPUTABLE and key in planned and found:
            world = planned[key]
            if "alias_of" in world:
                raise ExportError(f"{key}: aliased worlds are not exported")
            submitted = {
                name: union_reforms(
                    [
                        a["artifact"]["parameter_reform_routes"][name][
                            "submitted_reform"
                        ]
                        for a in found
                    ],
                    f"{key} {name}",
                )
                for name in ("baseline_world", "reform_world")
            }
            for name, field in (
                ("baseline_world", "baseline_reform"),
                ("reform_world", "reform_reform"),
            ):
                registry_side = replay.annual_reform(world[field])
                if key not in revisions and registry_side != submitted[name]:
                    raise ExportError(
                        f"{key}: the {name} the replay submitted is not the registry's construction"
                    )
                if (registry_side is None) != (submitted[name] is None):
                    raise ExportError(
                        f"{key}: {name} executed a world the registry does not declare"
                    )
            constructions = {a["artifact"]["construction"] for a in found}
            if constructions != {world["construction"]}:
                raise ExportError(f"{key}: artifacts disagree on the construction")
            entry_points = {}
            for name in ("baseline_world", "reform_world"):
                points = {
                    a["artifact"]["parameter_reform_routes"][name]["entry_point"]
                    for a in found
                }
                if len(points) != 1:
                    raise ExportError(
                        f"{key}: years disagree on the {name} entry point"
                    )
                entry_points[name] = points.pop()
            sentinels = sorted(
                {
                    path
                    for a in found
                    for path in a["artifact"]["null_executed_as_no_limit"]
                }
            )
            if sentinels != sorted(set(world.get("sentinels", []))):
                raise ExportError(
                    f"{key}: executed sentinels differ from the registry's"
                )
            entry["computed"] = True
            entry["construction"] = {
                "kind": world["construction"],
                "components": world["components"],
                "baseline_world": {
                    "entry_point": entry_points["baseline_world"],
                    "submitted_reform": submitted["baseline_world"],
                },
                "reform_world": {
                    "entry_point": entry_points["reform_world"],
                    "submitted_reform": submitted["reform_world"],
                },
                "construction_revision": revisions.get(key),
                "sentinels": sentinels,
                "executor_route": executor_route(
                    submitted["baseline_world"], submitted["reform_world"]
                ),
                "head_definitions": found[0]["artifact"]["head_definitions"],
            }
            for item in found:
                artifact = item["artifact"]
                if (
                    artifact["head_definitions"]
                    != entry["construction"]["head_definitions"]
                ):
                    raise ExportError(f"{key}: years disagree on the fiscal heads")
                entry["years"].append(
                    {
                        "year": artifact["year"],
                        "fy": artifact["fy_proxy"],
                        "measure_total_gbp": artifact["measure_total_gbp"],
                        "head_effects": artifact["head_effects"],
                        "processed_parameter_values": artifact[
                            "processed_parameter_values"
                        ],
                        "artifact": item["path"],
                        "artifact_sha256": item["sha256"],
                    }
                )
        elif found:
            raise ExportError(
                f"{key}: artifacts exist for a measure the registry does not compute"
            )
        elif key in idle:
            # Computable, but nothing to execute by design (worlds.not_computable).
            entry["reason"] = " ".join(filter(None, [entry["reason"], idle[key]]))
        if not entry["computed"] and any(r["status"] == CONSTRUCTED for r in obr_rows):
            raise ExportError(f"{key}: a noncomputed measure owns constructed OBR rows")
        measures.append(entry)
    if artifacts_by_measure:
        raise ExportError(
            f"{event}: artifacts for unregistered measures {sorted(artifacts_by_measure)}"
        )
    if seen_rows != set(rows_by_id):
        raise ExportError(f"{event}: COMPARISON.csv rows outside the registry")

    accounts = accounting(registry)
    accounts["computed"] = computed_accounting(measures, accounts["totals"])
    identity = namespace.record["identity"]
    return {
        "schema": SCHEMA,
        "semantics": SEMANTICS,
        "sign_convention": "positive_gain_to_exchequer",
        "event": {
            "slug": event,
            "name": registry["event_name"],
            "registry_path": run["registry_path"],
            "registry_sha256": registry_sha256,
        },
        "variant": {
            "variant_id": namespace.record["variant_id"],
            "variant_identity_sha256": namespace.record["identity_sha256"],
            "packages": {
                name: package["version"]
                for name, package in sorted(identity["packages"].items())
            },
            "dataset": {
                field: identity["dataset"][field]
                for field in ("repo_id", "path", "revision", "sha256")
            },
            "data_years": namespace.record["data_years"],
            "receipt_sha256": namespace.receipt_sha256,
            "namespace_manifest_sha256": namespace.manifest_sha256,
            "run_manifest_sha256": namespace.files[f"{event}/RUN_MANIFEST.json"],
            "comparison_sha256": namespace.files[f"{event}/COMPARISON.csv"],
        },
        "years": {
            "requested": run["requested_years"],
            "supported": run["supported_years"],
            "unsupported": run["unsupported_years"],
        },
        "accounting": accounts,
        "measures": measures,
    }


def write_export(
    record: dict,
    events: list[str] | None = None,
    *,
    root: Path = ROOT,
    output_root: Path | None = None,
) -> Path:
    """Write every event's export and the manifest of their digests."""
    namespace = Namespace(record, root=root)
    available = namespace.events()
    events = available if events is None else events
    unknown = sorted(set(events) - set(available))
    if unknown:
        raise ExportError(f"events not in {record['variant_id']}'s corpus: {unknown}")
    out = (output_root or root / EXPORT_ROOT.relative_to(ROOT)) / record["variant_id"]
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for event in sorted(events):
        data = canonical_json(build_event_export(namespace, event))
        (out / f"{event}.json").write_bytes(data)
        files[f"{event}.json"] = sha256_bytes(data)
    manifest = {
        "schema": SCHEMA,
        "variant_id": record["variant_id"],
        "variant_identity_sha256": record["identity_sha256"],
        "receipt_sha256": namespace.receipt_sha256,
        "files": files,
    }
    (out / EXPORT_MANIFEST).write_bytes(canonical_json(manifest))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--variant", help="variant id (default: newest certified)")
    parser.add_argument(
        "--events", nargs="*", help="event slugs (default: every replayed event)"
    )
    parser.add_argument(
        "--output-root", type=Path, help="default results/uk/dashboard_export"
    )
    args = parser.parse_args(argv)
    document = variants.load_document()
    record = (
        next((v for v in document["variants"] if v["variant_id"] == args.variant), None)
        if args.variant
        else default_variant(document)
    )
    if record is None:
        raise SystemExit(f"unknown variant {args.variant}")
    out = write_export(record, args.events, output_root=args.output_root)
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
