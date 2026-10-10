"""Index the installed policyengine-uk: raw parameter dates and variables.

Reads the parameter YAML tree exactly as written (policyengine-core's
`load_parameter_file`, before policyengine-uk's processing step backdates and
uprates it), so `earliest` is the first date key a file actually carries. Each
leaf records its YAML file, its dated values' instants, its label and its
uprating index. Variables are read with Python's AST from the installed
source. No model is initialized and no simulation runs.

Output: data/uk/events/pe_uk_parameter_dates_<version>.json.gz, the index
build_inventory.py resolves every cited parameter path against.

    uv run --with policyengine-uk==<version> python data/uk/events/index_pe_uk.py
"""

from __future__ import annotations

import gzip
import ast
import importlib.metadata as md
import json
from pathlib import Path

from policyengine_core.parameters import (
    Parameter,
    ParameterNode,
    ParameterScale,
    load_parameter_file,
)

HERE = Path(__file__).resolve().parent
PKG = Path(md.distribution("policyengine-uk").locate_file("policyengine_uk")).resolve()
PDIR = PKG / "parameters"


def rel(path: str | None) -> str | None:
    if not path:
        return None
    try:
        return str(Path(path).resolve().relative_to(PKG.parent))
    except ValueError:
        return path


def main() -> None:
    version = md.version("policyengine-uk")
    root = load_parameter_file(str(PDIR), name="")
    params, nodes, scales = [], [], []
    for p in root.get_descendants():
        name = p.name.lstrip(".")
        if isinstance(p, Parameter):
            dates = sorted(v.instant_str for v in p.values_list)
            meta = p.metadata or {}
            up = meta.get("uprating")
            params.append(
                {
                    "path": name,
                    "file": rel(getattr(p, "file_path", None)),
                    "earliest": dates[0] if dates else None,
                    "latest": dates[-1] if dates else None,
                    "dates": dates,
                    "label": meta.get("label"),
                    "unit": meta.get("unit"),
                    "uprating": up if isinstance(up, str) else (json.dumps(up, sort_keys=True) if up else None),
                }
            )
        elif isinstance(p, ParameterScale):
            scales.append(name)
            nodes.append(name)
        elif isinstance(p, ParameterNode):
            nodes.append(name)

    variables = []
    for file in sorted((PKG / "variables").rglob("*.py")):
        for cls in ast.parse(file.read_text()).body:
            if not isinstance(cls, ast.ClassDef) or not any(
                isinstance(base, ast.Name) and base.id == "Variable" for base in cls.bases
            ):
                continue
            attributes = {}
            for statement in cls.body:
                if isinstance(statement, ast.Assign):
                    for target in statement.targets:
                        if isinstance(target, ast.Name):
                            attributes[target.id] = statement.value
            def literal(name):
                value = attributes.get(name)
                return value.value if isinstance(value, ast.Constant) else None
            def identifier(name):
                value = attributes.get(name)
                return value.id.lower() if isinstance(value, ast.Name) else None
            variables.append({
                "name": cls.name, "file": rel(str(file)),
                "label": literal("label"), "entity": identifier("entity"),
                "definition_period": identifier("definition_period"),
                "has_formula": "formula" in attributes or any(isinstance(s, ast.FunctionDef) and
                    (s.name == "formula" or s.name.startswith("formula_")) for s in cls.body),
            })
    variables.sort(key=lambda v: v["name"])
    if len({v["name"] for v in variables}) != len(variables):
        raise ValueError("duplicate source variable names")
    out = {
        "policyengine_uk": version,
        "policyengine_core": md.version("policyengine-core"),
        "reader": "policyengine_core.parameters.load_parameter_file over the package parameters/ tree, before CountryTaxBenefitSystem.process_parameters",
        "variable_reader": "AST of direct Variable subclasses in installed variables/; source metadata, no processed system",
        "n_parameters": len(params),
        "n_scales": len(scales),
        "n_variables": len(variables),
        "parameters": sorted(params, key=lambda p: p["path"]),
        "nodes": sorted(nodes),
        "scales": sorted(scales),
        "variables": [v["name"] for v in variables],
        "variable_detail": variables,
    }
    dest = HERE / f"pe_uk_parameter_dates_{version}.json.gz"
    with gzip.GzipFile(dest, "wb", mtime=0) as fh:
        fh.write(json.dumps(out, sort_keys=True, indent=0).encode())
    print(f"wrote {dest.name}: {len(params)} parameters, {len(scales)} scales, {len(variables)} variables")


if __name__ == "__main__":
    main()
