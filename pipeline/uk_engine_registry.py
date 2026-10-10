"""Pinned UK engine introspection shared by fiscal-event registry builders."""

import importlib.metadata
import math


def engine_dumps(pin="2.89.2", system=None):
    """(parameter path -> 2026 value, variable name -> info, year probe)."""
    import policyengine_uk
    from policyengine_core.parameters import Parameter, ParameterNode, ParameterScale

    installed = importlib.metadata.version("policyengine-uk")
    if installed != pin:
        raise SystemExit(
            f"policyengine-uk {installed} installed, registry pinned to {pin}"
        )
    if system is None:
        system = policyengine_uk.CountryTaxBenefitSystem()
    params = {}

    def leaf(node, d="2026-06-01"):
        try:
            v = node(d)
        except Exception:  # noqa: BLE001 - preserve AB2025's missing-value probe
            return None
        if isinstance(v, float) and math.isinf(v):
            return "inf"
        if isinstance(v, float) and math.isnan(v):
            return None
        return v if isinstance(v, (int, float, str, bool)) else type(v).__name__

    def walk(node, prefix=""):
        if isinstance(node, ParameterScale):
            for i, b in enumerate(node.brackets):
                for attr in ("threshold", "rate", "amount"):
                    p = getattr(b, attr, None)
                    if p is not None:
                        params[f"{prefix}[{i}].{attr}"] = leaf(p)
            return
        if isinstance(node, Parameter):
            params[prefix] = leaf(node)
            return
        if isinstance(node, ParameterNode):
            for k in node.children:
                walk(node.children[k], f"{prefix}.{k}" if prefix else k)

    walk(system.parameters)
    variables = {
        n: {
            "entity": v.entity.key,
            "doc": (v.documentation or v.label or "")[:160],
        }
        for n, v in system.variables.items()
    }
    return params, variables
