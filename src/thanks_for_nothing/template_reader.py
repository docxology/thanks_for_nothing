# Copyright (c) 2026 Daniel Ari Friedman
"""Stage the admitted release composition for the pinned Template reader."""

import csv
import json
import re
from hashlib import sha256
from pathlib import Path
from typing import TypedDict, cast


class BoundInput(TypedDict):
    """One native source path and its digest."""

    path: str
    sha256: str


class PublicationSource(TypedDict):
    """Native receipt source inventory."""

    files: list[BoundInput]


class ReleaseReceipt(TypedDict):
    """Native receipt members needed by the reader."""

    products: dict[str, str]
    publication_source: PublicationSource


class CompositionLedger(TypedDict):
    """Original source and composed byte commitments."""

    templates: list[BoundInput]
    composed_sha256: str


SECTIONS = (
    ("01_abstract.md", "Abstract"),
    ("02_introduction.md", "Introduction"),
    ("03_methods.md", "Methods"),
    ("04_results.md", "Results"),
    ("05_discussion.md", "Discussion"),
    ("S01_supplement.md", "Supplementary information"),
    ("99_references.md", "References"),
)
RETAINED_BODY_FIGURES = 40
FRONT_MATTER = (
    ("graphical-abstract-meanings.png", "Conceptual graphical abstract"),
    ("graphical-abstract-experiments.png", "Experimental graphical abstract"),
    ("gnn-model-card.png", "GNN Bayesian model card"),
)
IMAGE = re.compile(
    r"""
    ^!\[(?P<caption>.+?)\]\([^\n)]*/figures/(?P<file>[\w-]+\.png)\)
    \{\#fig-(?P<label>[\w-]+)(?P<attributes>[^}]*)\}
    """,
    re.MULTILINE | re.VERBOSE,
)
EQUATION = re.compile(r"(?ms)^\$\$\n(.*?)^\$\$$")
EQUATION_LABEL = re.compile(r"\\label\{(eq:[\w-]+)\}")
NUMBER = re.compile(
    r"""
    (?<![A-Za-z0-9_@.-])-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?
    (?!(?:[A-Za-z0-9_-]|\.\d))
    """,
    re.VERBOSE,
)
INTERVAL = re.compile(r"\[([-+\u2212]?\d+(?:\.\d+)?), ([-+\u2212]?\d+(?:\.\d+)?)\]")
ATLAS = (
    "https://github.com/docxology/thanks_for_nothing/blob/"
    "9f0b85ee8c8333293ee5f0012c71a30f45a3b3b7/output/world_traditions.html"
)


def checked_bytes(path: Path, digest: str) -> bytes:
    """Read a retained member only when its release digest matches."""
    data = path.read_bytes()
    if sha256(data).hexdigest() != digest:
        msg = f"Retained reader input differs from the release receipt: {path.name}"
        raise ValueError(msg)
    return data


def composition(root: Path, receipt: ReleaseReceipt) -> str:
    """Admit the published composition and the exact text and citation sources."""
    output = root / "output"
    products = receipt["products"]
    report = "reports/manuscript_variables.json"
    ledger = cast("CompositionLedger", json.loads(checked_bytes(output / report, products[report])))
    for source in ledger["templates"]:
        _ = checked_bytes(root / source["path"], source["sha256"])
    source_digests = {item["path"]: item["sha256"] for item in receipt["publication_source"]["files"]}
    for name in ("references.bib", "assets/emptiness-cover-v0.3.png"):
        path = f"docs/manuscript/{name}"
        _ = checked_bytes(root / path, source_digests[path])
    source = checked_bytes(output / "reports/manuscript.md", products["reports/manuscript.md"])
    if sha256(source).hexdigest() != ledger["composed_sha256"]:
        msg = "Retained composed text differs from its native variable ledger"
        raise ValueError(msg)
    return source.decode()


def _labelled_equation(match: re.Match[str]) -> str:
    body = match[1]
    label = EQUATION_LABEL.search(body)
    if label is None:
        return match[0]
    expression = EQUATION_LABEL.sub("", body, count=1).strip()
    return f"$$\n{expression}\n$$ {{#{label[1]}}}"


def projected_sections(source: str) -> dict[str, str]:
    """Keep the original section sequence and normalize reader link syntax."""
    text = IMAGE.sub(
        r"![\g<caption>](../figures/\g<file>){#fig:\g<label>\g<attributes>}",
        source,
    )
    text = text.replace("](#fig-", "](#fig:").replace("](world_traditions.html)", f"]({ATLAS})")
    text = EQUATION.sub(_labelled_equation, text)
    # The shared PDF normalizer treats bare brackets containing plus signs as display math.
    text = INTERVAL.sub(r"$\\lbrack \1, \2 \\rbrack$", text)
    headings = list(re.finditer(r"(?m)^# (.+?)(?: \{[^}]+\})?$", text))
    if tuple(heading[1] for heading in headings) != tuple(title for _, title in SECTIONS):
        msg = "Retained composition does not have the complete expected section sequence"
        raise ValueError(msg)
    ends = [heading.start() for heading in headings[1:]] + [len(text)]
    return {
        filename: text[heading.start():end].strip() + "\n"
        for (filename, _), heading, end in zip(SECTIONS, headings, ends, strict=True)
    }


def stage_reader(root: Path) -> None:
    """Verify all retained inputs, then write the isolated reader projection."""
    output = root / "output"
    source = root / "docs/manuscript"
    receipt = cast(
        "ReleaseReceipt",
        json.loads((output / "reports/publication_build.json").read_bytes()),
    )
    products = receipt["products"]
    text = composition(root, receipt)
    sections = projected_sections(text)
    registry: list[dict[str, str]] = []
    for image in IMAGE.finditer(text):
        filename = image["file"]
        path = f"figures/{filename}"
        _ = checked_bytes(output / path, products[path])
        registry.append({
            "label": f"fig:{image['label']}", "filename": filename, "alt_text": image["caption"],
        })
    label_count = len({item["label"] for item in registry})
    if label_count != RETAINED_BODY_FIGURES or label_count != len(registry):
        msg = "Retained composition does not have its complete scientific figure inventory"
        raise ValueError(msg)

    front = ["# Archived graphical abstracts and model card"]
    additions = {"reader-cover.png": (source / "assets/emptiness-cover-v0.3.png").read_bytes()}
    for filename, caption in FRONT_MATTER:
        path = f"frontmatter/{filename}"
        additions[filename] = checked_bytes(output / path, products[path])
        label = "fig:" + Path(filename).stem
        registry.append({"label": label, "filename": filename, "alt_text": caption})
        front.append(f"![{caption}](../figures/{filename}){{#{label} width=90%}}")

    staging = output / "manuscript"
    staging.mkdir(parents=True, exist_ok=True)
    _ = (staging / "00_frontmatter.md").write_text("\n\n".join(front) + "\n")
    for filename, section in sections.items():
        _ = (staging / filename).write_text(section)
    _ = (staging / "config.yaml").write_bytes(
        b"# Generated manuscript ordering\n" + (source / "config.yaml").read_bytes(),
    )
    for name in ("references.bib", "preamble.md"):
        _ = (staging / name).write_bytes((source / name).read_bytes())
    for filename, data in additions.items():
        _ = (output / "figures" / filename).write_bytes(data)
    _ = (output / "figures/figure_registry.json").write_text(
        json.dumps({"schema_version": 1, "figures": registry}, indent=2) + "\n",
    )
    data = output / "data"
    data.mkdir(exist_ok=True)
    # Numeric parity uses the admitted release text, before reader transformations.
    with (data / "retained-reader-values.csv").open("w", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(("value", "source"))
        values = sorted({match[0] for match in NUMBER.finditer(text)})
        writer.writerows((value, "output/reports/manuscript.md") for value in values)


if __name__ == "__main__":
    stage_reader(Path(__file__).resolve().parents[2])
