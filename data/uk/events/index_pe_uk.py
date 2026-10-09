"""Index the installed policyengine-uk: raw parameter dates and variables.

Reads the parameter YAML tree exactly as written (policyengine-core's
`load_parameter_file`, before policyengine-uk's processing step backdates and
uprates it), so `earliest` is the first date key a file actually carries. Each
leaf records its YAML file, its dated values' instants, its label and its
uprating index. Variables come from the loaded tax-benefit system, with the
file each one is defined in.

Output: data/uk/events/pe_uk_parameter_dates_<version>.json.gz, the index
build_inventory.py resolves every cited parameter path against.

    uv run --with policyengine-uk==<version> python data/uk/events/index_pe_uk.py
"""

from __future__ import annotations

import gzip
import importlib.metadata as md
import inspect
import json
import os
from pathlib import Path

import policyengine_uk
from policyengine_core.parameters import (
    Parameter,
    ParameterNode,
    ParameterScale,
    load_parameter_file,
)

HERE = Path(__file__).resolve().parent
PKG = Path(policyengine_uk.__file__).resolve().parent
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

    from policyengine_uk import CountryTaxBenefitSystem

    system = CountryTaxBenefitSystem()
    variables = []
    for vname, var in sorted(system.variables.items()):
        try:
            vfile = rel(inspect.getsourcefile(type(var)))
        except TypeError:
            vfile = None
        variables.append(
            {
                "name": vname,
                "file": vfile,
                "label": getattr(var, "label", None),
                "entity": var.entity.key,
                "definition_period": str(var.definition_period),
                "has_formula": bool(var.formulas),
            }
        )
    out = {
        "policyengine_uk": version,
        "policyengine_core": md.version("policyengine-core"),
        "reader": "policyengine_core.parameters.load_parameter_file over the package parameters/ tree, before CountryTaxBenefitSystem.process_parameters",
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
