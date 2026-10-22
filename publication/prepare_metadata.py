import json
import re
import subprocess
from pathlib import Path

import yaml

root = Path.cwd()
meta = yaml.safe_load((root / "docs/manuscript/metadata.yaml").read_text())
source = (root / "output/reports/manuscript.md").read_text()
abstract = source.split("\n# Introduction", 1)[0].split("\n", 1)[1].strip()
if len(abstract.split("\n\n")) != 2:
    raise ValueError("The generated paper abstract must contain exactly two paragraphs")
if re.search(r"\{\{[A-Z]", abstract) is not None:
    raise ValueError("The paper abstract contains an unresolved scientific value")
if meta["repository-url"] not in abstract:
    raise ValueError("The paper abstract is missing its declared repository URL")
description = subprocess.run(
    ["pandoc", "--from=markdown", "--to=html5"], input=abstract,
    text=True, capture_output=True, check=True,
).stdout.strip()
metadata = {
    "title": meta["title"] + ": " + meta["subtitle"],
    "upload_type": "publication", "publication_type": "preprint",
    "publication_date": meta["date"], "version": meta["version"],
    "creators": [{"name": "Friedman, Daniel Ari", "orcid": meta["orcid"],
                  "affiliation": meta["affiliation"]}],
    "access_right": "open", "license": "cc-by-4.0", "description": description,
    "keywords": ["gratitude", "emptiness", "active inference", "model revisability",
                 "generalized notation notation", "reproducible research"],
    "notes": "Combined manuscript and single-commit code snapshot. Original paper and figures: "
             "CC BY 4.0. Original software and computational records: MIT. Third-party works "
             "retain their separate terms; see THIRD_PARTY.md. Original unlicensed notebooks "
             "and raw scholarly downloads are excluded; exact local acquisition is documented.",
    "related_identifiers": [{
        "identifier": meta["repository-url"] + "/releases/tag/v" + meta["version"],
        "relation": "hasPart", "scheme": "url",
    }],
}
(root / ".zenodo.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
(root / "publication/zenodo-metadata.json").write_text(
    json.dumps({"metadata": metadata}, indent=2, ensure_ascii=False) + "\n"
)
(root / "publication/abstract.md").write_text(abstract + "\n")
print(json.dumps({"abstract_paragraphs": 2, "version": meta["version"],
                  "doi": meta["doi"], "description_source": "generated paper abstract"}))
