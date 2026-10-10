"""Preserve the installed-source files cited by the inventory and targeted audit.

No model imports. Run: python collect_classification_evidence.py PACKAGE_DIR
The version and wheel identity are pinned separately in source_receipt.json.
"""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[3]
package=Path(sys.argv[1])
rows=[json.loads(x) for x in (ROOT/'data/uk/events/inventory.jsonl').read_text().splitlines()]
paths={p.removeprefix('policyengine_uk/') for r in rows for p in r['mechanism_evidence'] if p.startswith('policyengine_uk/')}
audit=(ROOT/'docs/uk_replay/research/CLASSIFICATION_AUDIT.md').read_text()
for match in re.findall(r'(?:variables|parameters|data|scenarios)/[\w/.-]+\.(?:py|yaml)',audit):
 if (package/match).is_file():paths.add(match)
paths.update(['simulation.py','scenarios/uc_reform.py','tax_benefit_system.py','utils/parameters.py','data/economic_assumptions.py'])
files={};missing=[]
for path in sorted(paths):
 p=package/path
 if not p.is_file():missing.append(path);continue
 b=p.read_bytes();files['policyengine_uk/'+path]={'sha256':hashlib.sha256(b).hexdigest(),'source':b.decode()}
version=json.loads((ROOT/'data/uk/events/source_receipt.json').read_text())['latest_pypi']
result={'engine':'policyengine-uk '+version,'basis':'installed wheel; selected inventory/audit source files, without model initialization','files':files,'missing_files':missing}
assert not missing,missing
(ROOT/'docs/uk_replay/evidence/classification_sources.json').write_text(json.dumps(result,sort_keys=True,indent=1)+'\n')
print('Preserved',len(files),'source files')
