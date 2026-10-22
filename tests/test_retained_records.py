# Copyright (c) 2026 Daniel Ari Friedman
import gzip
from hashlib import sha256

import pytest
from pydantic import ValidationError

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.retained_records import RetainedRecord, restore_records


def record(tmp_path):
    compressed = gzip.compress(b'{"value":1}')
    (tmp_path / "record.json.gz").write_bytes(compressed)
    return RetainedRecord(name="record.json", sha256=sha256(b'{"value":1}').hexdigest(),
                          gzip_sha256=sha256(compressed).hexdigest())


def test_exact_restore_and_idempotent_reuse(tmp_path):
    item = record(tmp_path)
    restore_records(tmp_path, (item,))
    target = tmp_path / item.name
    before = target.stat().st_mtime_ns
    restore_records(tmp_path, (item,))
    assert target.read_bytes() == b'{"value":1}'
    assert target.stat().st_mtime_ns == before


@pytest.mark.parametrize("boundary", ["transport", "content", "existing", "symlink", "directory"])
def test_fail_closed_without_replacing_existing(tmp_path, boundary):
    item = record(tmp_path)
    target = tmp_path / item.name
    if boundary == "transport":
        (tmp_path / "record.json.gz").write_bytes(b"damaged")
    elif boundary == "content":
        item = item.model_copy(update={"sha256": "0" * 64})
    elif boundary == "existing":
        target.write_bytes(b"changed")
    elif boundary == "symlink":
        target.symlink_to(tmp_path / "missing")
    else:
        target.mkdir()
    with pytest.raises(ContractError):
        restore_records(tmp_path, (item,))
    if boundary == "existing":
        assert target.read_bytes() == b"changed"
    elif boundary in {"transport", "content"}:
        assert not target.exists()


def test_rejects_traversal():
    with pytest.raises(ValidationError):
        RetainedRecord(name="../record.json", sha256="0" * 64, gzip_sha256="0" * 64)
