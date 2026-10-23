"""Certified replay variants: the exact worlds the event corpus may run on.

A variant is one certified policyengine.py bundle's execution identity: the
wrapper, model and core distributions, the release bundle the wrapper reports
under its packaged certification, and the certified dataset's bytes. The
runner validates the selected variant exactly before any simulation and
refuses every other combination; there is no flag that relaxes a check.
Running a newer engine means adding a variant whose certification names it.
See docs/uk_replay/RELEASE_REPLAY.md.

Engine-free: nothing here imports policyengine. Installed distributions are
read through importlib.metadata and their RECORD files.
"""

from __future__ import annotations

import base64
import hashlib
import importlib.metadata
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VARIANTS_PATH = ROOT / "data" / "uk" / "replay_variants.json"
CERTIFIED_BUNDLE = ROOT / "data" / "uk" / "certified_bundle.json"
LEGACY_RESULT_ROOT = "results/uk/events"
REPLAY_RESULT_ROOT = "results/uk/replays"
RUNTIME_ROOT = ROOT / ".venv-replay-checks" / "runtime"
RECEIPT_NAME = "REPLAY_RECEIPT.json"
PACKAGES = ("policyengine", "policyengine-uk", "policyengine-core")
PACKAGED_MANIFEST = "policyengine/data/bundle/manifest.json"
TOKEN_VARIABLES = ("HUGGING_FACE_TOKEN", "HF_TOKEN", "HUGGINGFACE_HUB_TOKEN")
OFFLINE_VARIABLES = {
    "HF_HUB_OFFLINE": "1",
    "HF_DATASETS_OFFLINE": "1",
    "TRANSFORMERS_OFFLINE": "1",
    "HF_HUB_DISABLE_TELEMETRY": "1",
    "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
}
# policyengine.py 6.x fetches the data release manifest with requests
# (provenance/manifest.py, get_data_release_manifest), which ignores
# HF_HUB_OFFLINE. requests reads these proxy variables, so with them the
# fetch fails at once and certify_data_release_compatibility falls back to
# the wrapper's packaged certification, the one each record certifies.
NO_NETWORK = {
    name: "http://127.0.0.1:9"
    for name in (
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "http_proxy",
        "https_proxy",
        "all_proxy",
    )
}
PROXY_EXCEPTIONS = ("NO_PROXY", "no_proxy")
# policyengine.py#704 lets POLICYENGINE_<COUNTRY>_DATA_MANIFEST_FILE select a
# local data release manifest in place of the fetched one. A replay must
# certify against the wrapper's packaged certification, never a file the
# host happens to point at, so isolation removes it for every country.
LOCAL_MANIFEST_VARIABLE = re.compile(r"POLICYENGINE_[A-Z0-9]+_DATA_MANIFEST_FILE")
ENGINE_MODULES = {
    "policyengine": "policyengine",
    "policyengine-uk": "policyengine_uk",
    "policyengine-core": "policyengine_core",
}
MATERIALIZATIONS = ("hf_cache_mirror", "policyengine_data_dir")
LAYOUTS = ("legacy_events", "replay_namespace")
STATUSES = ("certified", "candidate", "retired")
EXECUTORS = ("local", "modal")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
VERSION = re.compile(r"^[0-9]+(?:\.[0-9]+)*[a-z0-9.+-]*$")
PIN = re.compile(r"([A-Za-z0-9][A-Za-z0-9_.-]*)==([A-Za-z0-9_.+!-]+)")
# Installer bookkeeping differs between pip and uv for the same wheel; only
# the distribution's own files identify what was installed. Paths outside
# site-packages ("../../../bin/...") are console-script wrappers the
# installer generates, with the environment's interpreter in their shebang.
INSTALLER_METADATA = (
    "INSTALLER",
    "REQUESTED",
    "RECORD",
    "direct_url.json",
    "uv_cache.json",
)


class VariantError(ValueError):
    """A variant record, installed environment or dataset is not the certified one."""


def canonical_identity_bytes(value: object) -> bytes:
    """Sorted-key compact JSON. Identities hold strings, integers and nulls
    only, for which this equals RFC 8785; a test checks that equality."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode()


def identity_sha256(identity: dict) -> str:
    return hashlib.sha256(canonical_identity_bytes(identity)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def variant_slug(identity: dict) -> str:
    packages = identity["packages"]
    build = identity["release_bundle"]["certified_data_build_id"]
    return (
        f"pe{packages['policyengine']['version']}"
        f"_uk{packages['policyengine-uk']['version']}_{build}"
    )


def variant_id_for(identity: dict, taken: dict[str, str] | None = None) -> str:
    """The version slug, suffixed with the identity digest when another
    identity already holds that slug (same versions, other wheels or
    numerical environment)."""
    slug = variant_slug(identity)
    digest = identity_sha256(identity)
    holder = (taken or {}).get(slug)
    return slug if holder in (None, digest) else f"{slug}--{digest[:10]}"


def normalized_freeze(text: str, versions: dict[str, str]) -> str:
    """A freeze as exact pins. Engine packages installed from a verified local
    wheel or a commit appear as ``name @ <source>``; they become ``name==version``
    (the wheel and installed-file digests bind them) with the source kept as a
    comment. Any other non-pinned line refuses."""
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        name, at, source = stripped.partition(" @ ")
        key = re.sub(r"[-_.]+", "-", name).lower()
        if at and key in versions:
            lines.append(
                f"# {key} installed from {source.split('/')[-1] if source.startswith('file:') else source}"
            )
            lines.append(f"{key}=={versions[key]}")
        elif at:
            raise VariantError(f"freeze line is not an exact pin: {stripped}")
        else:
            lines.append(stripped)
    pins = requirements_pins("\n".join(lines))
    missing = sorted(set(versions) - set(pins))
    if missing:
        raise VariantError(f"freeze lacks {missing}")
    return "\n".join(lines) + "\n"


def hf_uri(dataset: dict) -> str:
    return f"hf://{dataset['repo_id']}/{dataset['path']}@{dataset['revision']}"


def requirements_pins(text: str) -> dict[str, str]:
    """Exact `name==version` lines only, normalised names; anything else refuses."""
    pins = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = PIN.fullmatch(line)
        if not match:
            raise VariantError(f"requirements must be exact pins, found {line!r}")
        name = re.sub(r"[-_.]+", "-", match.group(1)).lower()
        if name in pins:
            raise VariantError(f"duplicate requirement {name}")
        pins[name] = match.group(2)
    return pins


# --- the variant file -------------------------------------------------------


def load_document(path: Path = VARIANTS_PATH) -> dict:
    document = json.loads(path.read_bytes())
    if document.get("schema_version") != 1:
        raise VariantError("replay_variants.json schema_version must be 1")
    variants = document.get("variants")
    if not isinstance(variants, list) or not variants:
        raise VariantError("replay_variants.json lists no variants")
    ids = [variant.get("variant_id") for variant in variants]
    if len(ids) != len(set(ids)):
        raise VariantError("replay_variants.json repeats a variant_id")
    if document.get("default_variant") not in ids:
        raise VariantError("default_variant is not a listed variant")
    default = variants[ids.index(document["default_variant"])]
    if default.get("status") != "certified":
        raise VariantError("default_variant must be a certified variant")
    return document


def get_variant(
    variant_id: str | None = None,
    *,
    path: Path = VARIANTS_PATH,
    root: Path = ROOT,
    allow_uncertified: bool = False,
) -> dict:
    """The validated record; None selects the file's default variant.

    Only a certified variant runs, unless a qualification run, which replays
    its own candidate record, asks with ``allow_uncertified``."""
    document = load_document(path)
    wanted = variant_id or document["default_variant"]
    for record in document["variants"]:
        if record["variant_id"] == wanted:
            validate_record(record, root=root)
            if record["status"] != "certified" and not allow_uncertified:
                raise VariantError(
                    f"{wanted} is {record['status']}, not certified; only a "
                    "qualification run replays an uncertified variant"
                )
            return record
    raise VariantError(f"no replay variant {wanted!r}")


def is_legacy(record: dict) -> bool:
    """The populace-2023 world whose results keep their original layout."""
    return record["layout"] == "legacy_events"


def validate_record(record: dict, *, root: Path = ROOT) -> None:
    """Engine-free consistency: the record is one certified pairing."""
    problems = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            problems.append(message)

    try:
        identity = record["identity"]
        packages = identity["packages"]
        bundle = identity["release_bundle"]
        dataset = identity["dataset"]
        certification = record["certification"]
    except (KeyError, TypeError) as exc:
        raise VariantError(f"variant record is missing {exc}") from exc
    if not all(
        isinstance(part, dict)
        for part in (identity, packages, bundle, dataset, certification)
    ):
        raise VariantError(
            "identity, its packages, release_bundle and dataset, and "
            "certification must be objects"
        )
    need(
        set(packages) == set(PACKAGES),
        "identity.packages must name exactly the three packages",
    )
    for name in PACKAGES:
        package = packages.get(name) or {}
        need(
            isinstance(package.get("version"), str)
            and bool(VERSION.fullmatch(package.get("version", ""))),
            f"{name}: version",
        )
        need(
            bool(SHA256.fullmatch(str(package.get("record_sha256")))),
            f"{name}: record_sha256",
        )
        if "wheel_sha256" in package:
            need(
                bool(SHA256.fullmatch(str(package["wheel_sha256"]))),
                f"{name}: wheel_sha256",
            )
    if problems:
        raise VariantError("; ".join(problems))
    uk = packages["policyengine-uk"]["version"]
    wrapper = packages["policyengine"]["version"]
    need(
        record.get("variant_id")
        in (
            variant_slug(identity),
            f"{variant_slug(identity)}--{identity_sha256(identity)[:10]}",
        ),
        "variant_id differs from its identity",
    )
    need(
        record.get("identity_sha256") == identity_sha256(identity),
        "identity_sha256 differs",
    )
    need(
        bool(SHA256.fullmatch(str(identity.get("packaged_bundle_manifest_sha256")))),
        "packaged_bundle_manifest_sha256",
    )
    need(
        isinstance(bundle, dict)
        and all(value is None or isinstance(value, str) for value in bundle.values()),
        "release_bundle values must be strings or null",
    )
    need(
        bundle.get("model_package") == "policyengine-uk", "release_bundle model_package"
    )
    need(
        bundle.get("model_version") == uk,
        "release_bundle model_version differs from the installed model pin",
    )
    need(
        bundle.get("policyengine_version") == wrapper,
        "release_bundle policyengine_version differs from the wrapper pin",
    )
    need(
        certification.get("certified_for_model_version") == uk,
        "the certification does not name this model version",
    )
    need(
        certification.get("data_build_id") == bundle.get("certified_data_build_id"),
        "the certification names another data build",
    )
    need(
        certification.get("compatibility_basis") == bundle.get("compatibility_basis"),
        "certification compatibility_basis differs from the release bundle",
    )
    for field in ("repo_id", "repo_type", "revision", "path", "sha256", "size_bytes"):
        need(field in dataset, f"dataset.{field}")
    if problems:
        raise VariantError("; ".join(problems))
    need(dataset["repo_type"] in ("model", "dataset"), "dataset.repo_type")
    need(bool(SHA256.fullmatch(str(dataset["sha256"]))), "dataset.sha256")
    need(
        isinstance(dataset["size_bytes"], int) and dataset["size_bytes"] > 0,
        "dataset.size_bytes",
    )
    need(
        bundle.get("certified_data_artifact_sha256") == dataset["sha256"],
        "the certified artifact digest differs from the dataset",
    )
    need(
        bundle.get("default_dataset_uri") == hf_uri(dataset),
        "default_dataset_uri differs from the dataset",
    )
    need(
        identity.get("materialization") in MATERIALIZATIONS, "identity.materialization"
    )
    need(
        isinstance(identity.get("python"), str)
        and bool(re.fullmatch(r"3\.[0-9]+", identity.get("python", ""))),
        "identity.python",
    )
    need(record.get("status") in STATUSES, "status")
    need(record.get("layout") in LAYOUTS, "layout")
    need(
        isinstance(record.get("executor"), list)
        and bool(record["executor"])
        and set(record["executor"]) <= set(EXECUTORS),
        "executor",
    )
    years = record.get("data_years")
    need(
        isinstance(years, list)
        and bool(years)
        and all(isinstance(year, int) and not isinstance(year, bool) for year in years)
        and years == list(range(years[0], years[-1] + 1)),
        "data_years must be consecutive calendar years",
    )
    expected_root = (
        LEGACY_RESULT_ROOT
        if record.get("layout") == "legacy_events"
        else f"{REPLAY_RESULT_ROOT}/{record.get('variant_id')}"
    )
    need(
        record.get("result_root") == expected_root,
        f"result_root must be {expected_root}",
    )
    requirements = record.get("requirements") or {}
    need(
        identity.get("requirements_sha256") == requirements.get("sha256"),
        "the identity binds another requirements file",
    )
    requirements_path = root / str(requirements.get("path", ""))
    if not requirements.get("path") or not requirements_path.is_file():
        problems.append("requirements file is missing")
    else:
        payload = requirements_path.read_bytes()
        need(
            hashlib.sha256(payload).hexdigest() == requirements.get("sha256"),
            "requirements sha256 differs",
        )
        try:
            pins = requirements_pins(payload.decode())
        except VariantError as exc:
            problems.append(str(exc))
        else:
            for name in PACKAGES:
                need(
                    pins.get(name) == packages[name]["version"],
                    f"requirements pin {name}",
                )
    if record.get("layout") == "legacy_events":
        legacy = json.loads(
            (root / "data" / "uk" / "certified_bundle.json").read_bytes()
        )
        need(
            legacy.get("repo_id") == dataset["repo_id"]
            and legacy.get("artifact") == dataset["path"]
            and legacy.get("revision") == dataset["revision"]
            and legacy.get("revision") == bundle.get("certified_data_build_id")
            and legacy.get("sha256") == dataset["sha256"]
            and legacy.get("size_bytes") == dataset["size_bytes"],
            "the legacy variant differs from data/uk/certified_bundle.json",
        )
        need(
            any(
                row.get("name") == "policyengine-uk"
                and row.get("specifier") == f"=={uk}"
                for row in legacy.get("compatible_model_packages", [])
            ),
            "data/uk/certified_bundle.json does not declare this model version",
        )
    if problems:
        raise VariantError(f"{record.get('variant_id')}: " + "; ".join(problems))


# --- the installed environment ---------------------------------------------


def _record_rows(distribution) -> list[tuple[str, str, str]]:
    text = distribution.read_text("RECORD")
    if text is None:
        raise VariantError(f"{distribution.metadata['Name']}: no RECORD file")
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        path, digest, size = (line.rsplit(",", 2) + ["", ""])[:3]
        name = path.rsplit("/", 1)[-1]
        if (
            ".dist-info/" in path
            and name in INSTALLER_METADATA
            or "__pycache__/" in path
            or path.endswith(".pyc")
            or path.startswith("../")
        ):
            continue
        rows.append((path, digest, size))
    return sorted(rows)


def distribution_record_sha256(distribution, *, verify_files: bool = True) -> str:
    """Digest of the distribution's own RECORD entries, after checking every
    listed file on disk against its recorded hash. Installer bookkeeping and
    bytecode are excluded, so pip and uv installs of one wheel agree."""
    rows = _record_rows(distribution)
    if verify_files:
        for path, digest, size in rows:
            if not digest:
                raise VariantError(f"{path}: RECORD lists no hash")
            algorithm, _, expected = digest.partition("=")
            if algorithm != "sha256":
                raise VariantError(f"{path}: RECORD hash is not sha256")
            payload = Path(distribution.locate_file(path)).read_bytes()
            actual = (
                base64.urlsafe_b64encode(hashlib.sha256(payload).digest())
                .rstrip(b"=")
                .decode()
            )
            if actual != expected or (size and int(size) != len(payload)):
                raise VariantError(
                    f"installed file differs from its wheel RECORD: {path}"
                )
    body = "\n".join(",".join(row) for row in rows).encode()
    return hashlib.sha256(body).hexdigest()


def installed_distributions() -> dict[str, str]:
    """Version of each importable distribution. When a name appears twice on
    sys.path the first one is what Python imports (and what
    importlib.metadata.version reports), so the first wins here too: a
    host's own packages behind the pinned environment, such as Modal's
    client dependencies in its containers, do not count."""
    versions = {}
    for distribution in importlib.metadata.distributions():
        name = re.sub(r"[-_.]+", "-", distribution.metadata["Name"]).lower()
        versions.setdefault(name, distribution.version)
    return versions


def installed_identity(*, verify_files: bool = True) -> dict:
    packages = {}
    for name in PACKAGES:
        try:
            distribution = importlib.metadata.distribution(name)
        except importlib.metadata.PackageNotFoundError as exc:
            raise VariantError(f"{name} is not installed") from exc
        packages[name] = {
            "version": distribution.version,
            "record_sha256": distribution_record_sha256(
                distribution, verify_files=verify_files
            ),
        }
    manifest = Path(
        importlib.metadata.distribution("policyengine").locate_file(PACKAGED_MANIFEST)
    )
    return {
        "packages": packages,
        "packaged_bundle_manifest_sha256": sha256_file(manifest),
        "python": f"{sys.version_info.major}.{sys.version_info.minor}",
        "distributions": installed_distributions(),
        "unlisted_files": unlisted_package_files() if verify_files else {},
        "startup_files": startup_files() if verify_files else [],
    }


def unlisted_package_files(names=PACKAGES) -> dict[str, list[str]]:
    """Files and links in each package's top-level directories that the
    package's own RECORD does not list.

    A listed file is checked against its hash, but policyengine-core also
    loads files nobody listed: every file in a parameter directory and its
    subdirectories (parameters/parameter_node.py: sorted os.listdir, then
    os.path.isdir) and every module in a variable directory and its
    subdirectories (taxbenefitsystems/tax_benefit_system.py,
    add_variables_from_directory: glob "*.py", then glob "*/"). Both recurse
    into a ``__pycache__`` and follow a symlinked directory, so:

    * only conventionally named bytecode inside a ``__pycache__`` is skipped
      (BYTECODE_NAME; runs never import it: isolate_bytecode); anything else
      there, including a README.pyc that the parameter loader would read, is
      reported;
    * every symlink, to a file or a directory, is reported;
    * a file counts as listed only in its own package's RECORD, by its
      unresolved path: another distribution's RECORD is never hash-checked.
    """
    found = {}
    for name in names:
        distribution = importlib.metadata.distribution(name)
        rows = _record_rows(distribution)
        listed = {
            os.path.normpath(str(distribution.locate_file(row[0]))) for row in rows
        }
        tops = {
            row[0].split("/", 1)[0]
            for row in rows
            if "/" in row[0] and ".dist-info/" not in row[0]
        }
        root = str(distribution.locate_file(""))
        extra = []
        for top in sorted(tops):
            base = str(distribution.locate_file(top))
            if os.path.islink(base):
                extra.append(f"{top} (symlink)")
                continue
            for directory, subdirectories, files in os.walk(base):
                subdirectories.sort()
                cache = "__pycache__" in Path(directory).parts
                for entry in sorted([*subdirectories, *files]):
                    path = os.path.normpath(os.path.join(directory, entry))
                    relative = os.path.relpath(path, root)
                    if os.path.islink(path):
                        extra.append(f"{relative} (symlink)")
                    elif entry in subdirectories:
                        continue
                    elif cache and BYTECODE_NAME.fullmatch(entry):
                        continue
                    elif path not in listed:
                        extra.append(relative)
        if extra:
            found[name] = extra
    return found


VIRTUALENV_SHIM = ("_virtualenv.pth", "import _virtualenv")
# The names import writes into a __pycache__ (importlib.util.cache_from_source:
# <module>.<cache_tag>[.opt-<n>].pyc). parameter_node.py reads any file whose
# stem is README before it filters extensions; every name this pattern
# matches has at least two dots, so its stem is never README.
BYTECODE_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\.[a-z]+-[0-9]+(\.opt-[0-9]+)?\.pyc")


def startup_files(names=PACKAGES) -> list[dict]:
    """The ``*.pth`` files beside the engine packages. Python runs their
    ``import`` lines at startup (site.py), before any check here, so each
    must belong to a pinned distribution or be the virtual environment's
    own shim; verify_installed decides."""
    owners = {}
    for distribution in importlib.metadata.distributions():
        owner = re.sub(r"[-_.]+", "-", distribution.metadata["Name"]).lower()
        for line in (distribution.read_text("RECORD") or "").splitlines():
            relative = line.rsplit(",", 2)[0]
            if relative.endswith(".pth"):
                owners[os.path.normpath(str(distribution.locate_file(relative)))] = (
                    owner
                )
    sites = sorted(
        {str(importlib.metadata.distribution(name).locate_file("")) for name in names}
    )
    out = []
    for site in sites:
        for entry in sorted(os.listdir(site)):
            if not entry.endswith(".pth"):
                continue
            path = os.path.normpath(os.path.join(site, entry))
            out.append(
                {
                    "name": entry,
                    "owner": owners.get(path),
                    "text": Path(path).read_text(errors="replace").strip()[:200],
                    "symlink": os.path.islink(path),
                }
            )
    return out


def startup_file_problems(files: list[dict], pins: dict[str, str]) -> list[str]:
    problems = []
    for file in files:
        shim = (file["name"], file["text"]) == VIRTUALENV_SHIM
        if file.get("symlink") or not (shim or file["owner"] in pins):
            problems.append(
                f"startup file {file['name']} belongs to no pinned distribution"
            )
    return problems


def isolate_bytecode(runtime_root: Path, environ=os.environ) -> Path:
    """Compile the engine from its verified sources, never from a cache.

    Bytecode is read only from sys.pycache_prefix when one is set, so an
    empty prefix with writing turned off ignores every __pycache__ beside
    the sources (including one whose header matches its source). Spawned
    year workers inherit both settings. Call before importing the engine."""
    loaded = sorted(m for m in ENGINE_MODULES.values() if m in sys.modules)
    if loaded:
        raise VariantError(f"engine modules imported before isolation: {loaded}")
    prefix = runtime_root.resolve() / "no-bytecode"
    if prefix.is_symlink():  # before anything resolves or removes it
        raise VariantError(f"{prefix} is a symlink; refusing it")
    if prefix.exists():
        shutil.rmtree(prefix)
    prefix.mkdir(parents=True)
    sys.pycache_prefix = str(prefix)
    sys.dont_write_bytecode = True
    environ["PYTHONPYCACHEPREFIX"] = str(prefix)
    environ["PYTHONDONTWRITEBYTECODE"] = "1"
    return prefix


def verify_import_origins(names=PACKAGES) -> None:
    """Each imported engine package is the verified distribution's own
    files, not a same-named tree earlier on sys.path."""
    for name in names:
        module_name = ENGINE_MODULES[name]
        module = sys.modules.get(module_name)
        if module is None:
            raise VariantError(f"{module_name} is not imported yet")
        expected = Path(
            importlib.metadata.distribution(name).locate_file(
                f"{module_name}/__init__.py"
            )
        ).resolve()
        if Path(module.__file__).resolve() != expected:
            raise VariantError(
                f"{module_name} imported from {module.__file__}, not its "
                f"verified distribution ({expected})"
            )


def environment_mismatches(pins: dict[str, str], installed: dict) -> list[str]:
    """Every pinned distribution installed at its pinned version. Extra
    distributions (the receipt tools) are allowed; a missing or different
    numerical dependency is not."""
    have = installed.get("distributions", {})
    return [
        f"{name}: pinned {version}, installed {have.get(name)}"
        for name, version in sorted(pins.items())
        if have.get(name) != version
    ]


def identity_mismatches(record: dict, installed: dict) -> list[str]:
    identity = record["identity"]
    out = []
    for name in PACKAGES:
        want = identity["packages"][name]
        have = installed["packages"].get(name, {})
        for field in ("version", "record_sha256"):
            if want[field] != have.get(field):
                out.append(
                    f"{name} {field}: certified {want[field]}, installed {have.get(field)}"
                )
    if (
        identity["packaged_bundle_manifest_sha256"]
        != installed["packaged_bundle_manifest_sha256"]
    ):
        out.append(
            "packaged bundle manifest: certified "
            f"{identity['packaged_bundle_manifest_sha256']}, installed "
            f"{installed['packaged_bundle_manifest_sha256']}"
        )
    if identity["python"] != installed["python"]:
        out.append(
            f"python: certified {identity['python']}, running {installed['python']}"
        )
    return out


def verify_installed(
    record: dict, *, installed: dict | None = None, root: Path = ROOT
) -> dict:
    installed = installed if installed is not None else installed_identity()
    mismatches = identity_mismatches(record, installed)
    pins = requirements_pins((root / record["requirements"]["path"]).read_text())
    mismatches += environment_mismatches(pins, installed)
    mismatches += [
        f"{name}: files outside its RECORD: {', '.join(paths[:5])}"
        + (f" and {len(paths) - 5} more" if len(paths) > 5 else "")
        for name, paths in sorted(installed.get("unlisted_files", {}).items())
    ]
    mismatches += startup_file_problems(installed.get("startup_files", []), pins)
    if mismatches:
        raise VariantError(
            f"{record['variant_id']}: installed environment is not the certified one: "
            + "; ".join(mismatches)
        )
    return installed


def isolate_certification_environment(environ=os.environ) -> list[str]:
    """Use the wrapper's packaged certification on every host.

    With a Hugging Face token, policyengine.py derives the certification from
    the remote release manifest instead, which changes release_bundle fields
    (OFFLINE_BUNDLE_AUDIT.json records the 5.0.2 case; 6.2.6 behaves alike).
    Without a token a private data repository answers 401; a public one
    would still answer, so the proxy variables (NO_NETWORK) make the fetch
    fail for both. A local data release manifest setting
    (LOCAL_MANIFEST_VARIABLE) is removed too. Call before importing
    policyengine; returns the variables removed."""
    local_manifests = sorted(
        name for name in environ if LOCAL_MANIFEST_VARIABLE.fullmatch(name)
    )
    removed = [
        name
        for name in (*TOKEN_VARIABLES, *PROXY_EXCEPTIONS, *local_manifests)
        if environ.pop(name, None) is not None
    ]
    environ.update(OFFLINE_VARIABLES)
    environ.update(NO_NETWORK)
    return removed


def verify_release_bundle(record: dict, bundle: dict) -> None:
    expected = record["identity"]["release_bundle"]
    if dict(bundle) != expected:
        differences = {
            key: {"certified": expected.get(key), "runtime": bundle.get(key)}
            for key in sorted(set(expected) | set(bundle))
            if expected.get(key) != bundle.get(key)
        }
        raise VariantError(
            f"{record['variant_id']}: runtime release bundle differs: {differences}"
        )


# --- the dataset --------------------------------------------------------------


def _cache_candidates(dataset: dict, hub_cache: Path) -> list[Path]:
    owner, name = dataset["repo_id"].split("/", 1)
    prefix = "models" if dataset["repo_type"] == "model" else "datasets"
    snapshots = hub_cache / f"{prefix}--{owner}--{name}" / "snapshots"
    return sorted(snapshots.glob(f"*/{dataset['path']}")) if snapshots.is_dir() else []


def find_dataset_bytes(record: dict, *, source: Path | None = None) -> Path:
    """A local file holding the certified bytes, found by digest, never by name."""
    dataset = record["identity"]["dataset"]
    hub_cache = Path(
        os.environ.get("HF_HUB_CACHE")
        or Path(os.environ.get("HF_HOME", Path.home() / ".cache" / "huggingface"))
        / "hub"
    )
    candidates = (
        [source] if source is not None else _cache_candidates(dataset, hub_cache)
    )
    for candidate in candidates:
        path = Path(candidate)
        if (
            path.is_file()
            and path.stat().st_size == dataset["size_bytes"]
            and sha256_file(path) == dataset["sha256"]
        ):
            return path
    raise VariantError(
        f"{record['variant_id']}: no local file holds the certified dataset "
        f"{dataset['path']} (sha256 {dataset['sha256']}); searched {[str(c) for c in candidates]}"
    )


def materialize_dataset(
    record: dict, runtime_root: Path | None = None, *, source: Path | None = None
) -> Path:
    """Place verified certified bytes where policyengine.py 6.x looks: the
    runtime directory's ./data/<file> (provenance/dataset_materialization.py,
    DEFAULT_DATA_DIR). Returns the absolute path."""
    if record["identity"]["materialization"] != "policyengine_data_dir":
        raise VariantError(
            f"{record['variant_id']} does not materialise into a data dir"
        )
    dataset = record["identity"]["dataset"]
    runtime_root = (runtime_root or RUNTIME_ROOT / record["variant_id"]).resolve()
    destination = runtime_root / "data" / Path(dataset["path"]).name
    for path in (runtime_root / "data", destination):
        if path.is_symlink():
            raise VariantError(f"{path} is a symlink; refusing it")
    if destination.resolve().parent != (runtime_root / "data").resolve():
        raise VariantError("dataset destination escapes the runtime directory")
    if (
        destination.is_file()
        and destination.stat().st_size == dataset["size_bytes"]
        and sha256_file(destination) == dataset["sha256"]
    ):
        return destination
    origin = find_dataset_bytes(record, source=source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(dir=destination.parent, prefix=".materialize-")
    os.close(handle)
    temporary = Path(temporary)
    try:
        shutil.copyfile(origin, temporary)
        if sha256_file(temporary) != dataset["sha256"]:
            raise VariantError("dataset copy failed SHA-256 verification")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination


# --- years and namespaces -----------------------------------------------------


def supported_years(record: dict, registry_years) -> tuple[list[int], list[dict]]:
    """Partition an event's registry years by the variant's data years."""
    data = record["data_years"]
    supported = sorted(
        year for year in set(registry_years) if data[0] <= year <= data[-1]
    )
    unsupported = [
        {
            "year": year,
            "reason": "before_data_year" if year < data[0] else "after_extension_end",
        }
        for year in sorted(set(registry_years))
        if not data[0] <= year <= data[-1]
    ]
    return supported, unsupported


def namespace_root(record: dict, *, root: Path = ROOT) -> Path:
    return root / record["result_root"]


def event_output_dir(record: dict, event: str, *, root: Path = ROOT) -> Path:
    return namespace_root(record, root=root) / event


CORPUS_NAME = "CORPUS.json"


def namespace_events(root: Path) -> list[str]:
    """The registered events a namespace's premises and summary cover.

    A qualification run records its corpus in CORPUS.json before replaying
    any event, so its event set never depends on which events produced
    results: a sealed namespace whose events all failed regenerates the same
    bytes after another event is registered. Without that record (the legacy
    namespace, or an inventory namespace that holds no run), the events it
    holds results for (an event directory with RUN_MANIFEST.json), or every
    registered event when it holds none."""
    from pipeline.build_uk_event_registry import EVENTS

    registered = list(EVENTS)
    corpus = root / CORPUS_NAME
    if corpus.is_file():
        listed = json.loads(corpus.read_bytes())["events"]
        unknown = sorted(set(listed) - set(registered))
        if unknown:
            raise VariantError(f"{corpus}: unregistered events {unknown}")
        return [event for event in registered if event in listed]
    held = [e for e in registered if (root / e / "RUN_MANIFEST.json").is_file()]
    return held or registered


def sealing_receipt(path: Path, *, root: Path = ROOT) -> Path | None:
    """The REPLAY_RECEIPT.json sealing a directory or one of its parents."""
    path = path.resolve()
    root = root.resolve()
    for directory in (path, *path.parents):
        if (directory / RECEIPT_NAME).is_file():
            return directory / RECEIPT_NAME
        if directory == root:
            break
    return None


def assert_not_sealed(path: Path, *, root: Path = ROOT) -> None:
    receipt = sealing_receipt(path, root=root)
    if receipt is not None:
        raise VariantError(
            f"{path} is inside a sealed replay namespace ({receipt}); write a new namespace"
        )


def manifest_fields(
    record: dict, registry_years, full_pairs, supported_pairs, artifact_pairs
) -> dict:
    """RUN_MANIFEST additions for a non-legacy variant (RELEASE_REPLAY.md)."""
    supported, unsupported = supported_years(record, registry_years)
    return {
        "variant_id": record["variant_id"],
        "variant_identity_sha256": record["identity_sha256"],
        "data_years": record["data_years"],
        "supported_years": supported,
        "unsupported_years": unsupported,
        "full_supported_grid": [
            {"measure_key": key, "year": year} for key, year in sorted(supported_pairs)
        ],
        "full_supported_grid_complete": set(supported_pairs) <= set(artifact_pairs),
    }
