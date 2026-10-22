# Copyright (c) 2026 Daniel Ari Friedman
from dataclasses import replace

import matplotlib.pyplot as plt
import numpy as np
import pytest

from thanks_for_nothing.contracts import ContractError
from thanks_for_nothing.gnn_figures import _tensor_table, require_table_clearance
from thanks_for_nothing.gnn_graphs import GraphCatalog, ModelGraph
from thanks_for_nothing.specifications import load_model


def test_inventory_clearance_rejects_the_reproduced_long_annotation():
    admitted = load_model("gratitude")
    shapes = tuple(
        (name, np.asarray(value).shape) for name, value in admitted.tensors.model_dump().items()
    )
    row = ModelGraph(
        admitted.model_id,
        admitted.source_hash,
        (),
        (),
        shapes,
        "Local / recall_world",
        "",
        "",
    )
    rows = tuple(replace(row, execution=f"Local / family_{i}") for i in range(21))
    catalog = GraphCatalog("geometry-control", "", "", rows, ())
    with pytest.raises(ContractError, match="requires complete runtime"):
        _tensor_table(replace(catalog, models=()))
    fig = _tensor_table(catalog)
    try:
        require_table_clearance(fig)
        annotation = next(text for text in fig.axes[0].texts if "instance(s)" in text.get_text())
        annotation.set_text("1 complete instance(s) / same shapes")
        with pytest.raises(ContractError, match="inventory text overlaps"):
            require_table_clearance(fig)
    finally:
        plt.close(fig)
