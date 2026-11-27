# Copyright (c) 2026 Daniel Ari Friedman
from hashlib import sha256

import pytest

from thanks_for_nothing.template_reader import SECTIONS, checked_bytes, projected_sections


def test_reader_relocates_paths_and_cross_references() -> None:
    source = "\n\n".join(f"# {title} {{#sec-{index}}}" for index, (_, title) in enumerate(SECTIONS))
    source += (
        "\n\n![Caption](../../tmp/release/figures/example.png){#fig-example width=90%}"
        "\n\n[Figure](#fig-example) and [equation](#eq:example), with interval [+0.1, +0.2]."
        "\n\n$$\n\\label{eq:example}\na = b\n$$\n"
        "\n$$\na = b\n\\label{eq:last-line}\n$$\n"
    )

    projection = projected_sections(source)
    assert tuple(projection) == tuple(name for name, _ in SECTIONS)
    assert "](../figures/example.png){#fig:example " in projection["99_references.md"]
    assert "[Figure](#fig:example)" in projection["99_references.md"]
    assert "$$ {#eq:example}" in projection["99_references.md"]
    assert "$$ {#eq:last-line}" in projection["99_references.md"]
    assert r"$\lbrack +0.1, +0.2 \rbrack$" in projection["99_references.md"]


def test_reader_refuses_a_changed_publication_member(tmp_path) -> None:
    member = tmp_path / "frozen.md"
    digest = sha256(b"admitted source").hexdigest()
    member.write_bytes(b"admitted source")
    assert checked_bytes(member, digest) == b"admitted source"
    member.write_bytes(b"altered source")
    with pytest.raises(ValueError, match="differs from the release receipt"):
        checked_bytes(member, digest)
