# Copyright (c) 2026 Daniel Ari Friedman
from xml.etree.ElementTree import Element

def fromstring(
    text: str,
    forbid_dtd: bool = ...,
    forbid_entities: bool = ...,
    forbid_external: bool = ...,
) -> Element: ...
