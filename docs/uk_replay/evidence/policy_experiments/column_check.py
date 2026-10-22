"""Which of the named variables an HDF5 dataset carries. Prints names and
presence only, never values.

    uvx --with h5py python -I column_check.py <dataset.h5> [...]
"""

import sys

import h5py

NAMES = (
    "self_employment_gross_receipts",
    "uses_property_allowance",
    "self_employment_income",
    "property_income",
)


def names(path: str) -> set[str]:
    found: set[str] = set()
    with h5py.File(path, "r") as handle:
        handle.visit(lambda key: found.update(part for part in key.split("/")))
    return found


for path in sys.argv[1:]:
    present = names(path)
    print(path)
    for name in NAMES:
        print(f"  {name}: {'present' if name in present else 'absent'}")
