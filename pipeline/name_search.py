"""The name-search string a UK measure registry records for a search pattern.

Pure: it takes the engine's parameter paths and variable names as given, so
tests run it without policyengine-uk installed.
"""

import re


def name_search(pattern, parameters, variables, pin):
    rx = re.compile(pattern, re.I)
    ph = [p for p in parameters if rx.search(p) and not p.startswith("baseline.")]
    # policyengine-core adds variables in glob order, which differs by
    # filesystem, so we sort them.
    vh = sorted(v for v in variables if rx.search(v))
    return (
        f"Searched BOTH the parameter tree and the VARIABLE list for /{pattern}/. "
        f"Parameters: {len(ph)} node(s) {ph[:6]}. Variables: {len(vh)} {vh[:6]}. "
        "Both are searched because a parameter-only search misses a variable "
        f"(#106). Re-run at policyengine-uk {pin}."
    )
