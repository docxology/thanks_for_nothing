# Copyright (c) 2026 Daniel Ari Friedman
"""Admit author identity and render a cover without inventing publication identifiers."""

import re
from pathlib import Path
from typing import ClassVar, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.provenance import file_digest


class _CoverProvenance(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    path: str
    sha256: str
    width: int = Field(gt=0)
    height: int = Field(gt=0)
    role: Literal["conceptual cover artwork"]
    scientific_data: Literal[False]
    generated_with: str = Field(min_length=1)
    generated_on: str
    brief: str = Field(min_length=1)


class PublicationMetadata(BaseModel):
    """One-author manuscript metadata shared by both rendered cover formats."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    title: str = Field(min_length=1)
    subtitle: str = Field(min_length=1)
    author: tuple[str, ...] = Field(min_length=1, max_length=1)
    date: str
    version: str
    paper_license: Literal["CC BY 4.0"] = Field(alias="paper-license")
    paper_license_url: Literal["https://creativecommons.org/licenses/by/4.0/"] = Field(
        alias="paper-license-url"
    )
    code_license: Literal["MIT"] = Field(alias="code-license")
    affiliation: str = Field(min_length=1)
    orcid: str
    email: str
    doi: str | None
    doi_status: Literal["assigned", "unassigned", "reserved"] = Field(alias="doi-status")
    zenodo_draft: str | None = Field(default=None, alias="zenodo-draft")
    cover_image: str = Field(alias="cover-image")
    cover_alt: str = Field(alias="cover-alt", min_length=1)
    cover_credit: str = Field(alias="cover-credit", min_length=1)
    cover_kicker: str = Field(alias="cover-kicker", min_length=1)
    cover_summary: str = Field(alias="cover-summary", min_length=1)
    repository_url: str = Field(alias="repository-url", pattern=r"^https://github\.com/[\w.-]+/[\w.-]+$")
    pdf_margin_mm: float = Field(alias="pdf-margin-mm", ge=5, le=25)
    pdf_footer_offset_mm: float = Field(alias="pdf-footer-offset-mm", gt=0, le=5)
    pdf_body_font_pt: float = Field(alias="pdf-body-font-pt", ge=9, le=12)
    graphical_abstracts: bool = Field(default=False, alias="graphical-abstracts")

    @property
    def doi_display(self) -> str:
        """Distinguish an unpublished reservation from registered and unassigned identifiers."""
        if self.doi_status == "reserved":
            return f"{self.doi} (reserved; unpublished draft)"
        return self.doi or "not assigned (private manuscript)"

    @property
    def doi_url(self) -> str | None:
        """Link a reservation to its private draft until a registered DOI can resolve."""
        match self.doi_status:
            case "reserved":
                return self.zenodo_draft
            case "assigned":
                return f"https://doi.org/{self.doi}"
            case "unassigned":
                return None


def valid_orcid(value: str) -> bool:
    """Check the ORCID ISO 7064 MOD 11-2 check digit, not merely its shape."""
    if re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", value) is None:
        return False
    digits = value.replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    check = (12 - total % 11) % 11
    return digits[-1] == str(check).replace("10", "X")


def load_publication(root: Path) -> PublicationMetadata:
    """Reject inconsistent identifiers and cover paths outside the research source."""
    raw = (root / "docs/manuscript/metadata.yaml").read_text()
    metadata = PublicationMetadata.model_validate(yaml.safe_load(raw))
    image = (root / metadata.cover_image).resolve()
    if not image.is_relative_to(root.resolve()) or not image.is_file():
        message = "Cover image must be an existing research-source file"
        raise ContractError(message)
    provenance = _CoverProvenance.model_validate_json(
        (root / "docs/manuscript/assets/cover-provenance.json").read_text()
    )
    header = image.read_bytes()[:24]
    if (
        provenance.path != metadata.cover_image
        or file_digest(image) != provenance.sha256
        or header[:8] != b"\x89PNG\r\n\x1a\n"
        or int.from_bytes(header[16:20], "big") != provenance.width
        or int.from_bytes(header[20:24], "big") != provenance.height
    ):
        message = "Cover illustration differs from its conceptual-art provenance"
        raise ContractError(message)
    if not valid_orcid(metadata.orcid):
        message = "Author ORCID has an invalid check digit"
        raise ContractError(message)
    if metadata.pdf_footer_offset_mm * 72 / 25.4 < metadata.pdf_body_font_pt + 2:
        message = "Footer offset must reserve the body font height and 2 pt clearance"
        raise ContractError(message)
    if (metadata.doi is None) != (metadata.doi_status == "unassigned") or (
        metadata.doi is not None and re.fullmatch(r"10\.\d{4,9}/\S+", metadata.doi) is None
    ):
        message = "Manuscript DOI and assignment status disagree"
        raise ContractError(message)
    if metadata.doi_status == "reserved":
        draft = re.fullmatch(
            r"https://zenodo\.org/(?:uploads|deposit)/([0-9]+)/?", metadata.zenodo_draft or ""
        )
        if draft is None or metadata.doi != f"10.5281/zenodo.{draft.group(1)}":
            message = "Reserved DOI must bind its production Zenodo draft"
            raise ContractError(message)
    return metadata


def _tex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(character, character) for character in value)


def write_cover_header(
    root: Path,
    output: Path,
    abstract_images: tuple[tuple[Path, tuple[tuple[str, str], ...]], ...] = (),
) -> Path:
    """Replace the standard title block with a dedicated, metadata-bound cover page."""
    meta = load_publication(root)
    image = (root / meta.cover_image).resolve().as_posix()
    doi = _tex(meta.doi_display)
    if meta.doi_url is not None:
        doi = rf"\href{{{_tex(meta.doi_url)}}}{{{doi}}}"
    cover = "\n".join(
        (
            r"\usepackage{graphicx}",
            r"\setkeys{Gin}{keepaspectratio=true}",
            r"\usepackage{float}",
            r"\usepackage{etoolbox}",
            (
                r"\apptocmd{\tableofcontents}{\clearpage}{}{\PackageError{thanks-for-nothing}"
                r"{Cannot separate contents from manuscript}{}}"
            ),
            r"\floatplacement{figure}{H}",
            r"\AtBeginEnvironment{CSLReferences}{\small\interlinepenalty=10000}",
            r"\setlength{\emergencystretch}{5em}",
            r"\renewcommand{\maketitle}{\begin{titlepage}\thispagestyle{empty}\centering",
            r"\begin{minipage}{0.91\textwidth}\raggedright",
            r"\vspace*{6mm}",
            rf"{{\sffamily\fontsize{{8}}{{11}}\selectfont {_tex(meta.cover_kicker)}\par}}",
            r"\vspace{7mm}",
            rf"{{\sffamily\bfseries\fontsize{{42}}{{46}}\selectfont {_tex(meta.title)}\par}}",
            r"\vspace{4mm}",
            rf"{{\sffamily\fontsize{{17}}{{22}}\selectfont {_tex(meta.subtitle)}\par}}",
            r"\vspace{5mm}",
            rf"{{\sffamily\fontsize{{10}}{{14}}\selectfont {_tex(meta.cover_summary)}\par}}",
            r"\vspace{7mm}",
            rf"\includegraphics[width=\linewidth,height=122mm,keepaspectratio]{{\detokenize{{{image}}}}}\par",
            r"\vspace{2mm}",
            rf"{{\scriptsize {_tex(meta.cover_credit)}\par}}",
            r"\vspace{7mm}",
            rf"{{\large\bfseries {_tex(meta.author[0])}\par}}",
            rf"{_tex(meta.affiliation)}\par",
            rf"\href{{https://orcid.org/{meta.orcid}}}{{ORCID: {meta.orcid}}}\par",
            rf"\href{{mailto:{_tex(meta.email)}}}{{{_tex(meta.email)}}}\par",
            r"\vspace{4mm}",
            rf"Code and reproducibility materials: \url{{{meta.repository_url}}}\par",
            r"\vspace{3mm}",
            rf"DOI: {doi}\par",
            r"\vspace{6mm}",
            (
                rf"{{\small Research manuscript, version {_tex(meta.version)}"
                rf"\quad {_tex(meta.date)}\par}}"
            ),
            "".join(
                (
                    rf"{{\small Paper: \href{{{meta.paper_license_url}}}{{{meta.paper_license}}}; ",
                    rf"original code: {meta.code_license}. Third-party rights remain separate.\par}}",
                )
            ),
            r"\end{minipage}\end{titlepage}",
            *(
                "".join(
                    (
                        r"\thispagestyle{empty}\noindent\includegraphics[width=\textwidth,",
                        rf"height=0.96\textheight,keepaspectratio]{{\detokenize{{{path.resolve().as_posix()}}}}}",
                        r"\par{\footnotesize Evidence: ",
                        r"\quad".join(
                            (
                                rf"\href{{{anchor}}}{{{_tex(title)}}}"
                                if anchor.startswith("frontmatter/")
                                else rf"\hyperref[{anchor}]{{{_tex(title)}}}"
                            )
                            for title, anchor in links
                        ),
                        r"\par}\clearpage",
                    )
                )
                for path, links in abstract_images
            ),
            r"\setcounter{page}{1}}",
        )
    )
    path = output / "reports/cover.tex"
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(cover + "\n")
    return path
