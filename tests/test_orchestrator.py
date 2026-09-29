import pytest
from common.schema import Filesystem, Medium, DeletedFileRecord, EffortLevel
from predictor.model import CaseAdaptiveModel
from recovery_engine.strategies import cost, value
from recovery_engine.orchestrator import allocate_within_budget, rank_allocations

def test_cost_value_monotonicity():
    size = 10_000_000  # 10 MB
    c_skip = cost(size, EffortLevel.SKIP)
    c_hdr = cost(size, EffortLevel.HEADER_CHECK)
    c_scoped = cost(size, EffortLevel.SCOPED_CARVE)
    c_full = cost(size, EffortLevel.FULL_CARVE)

    assert c_skip < c_hdr < c_scoped < c_full

    v_hdr = value(0.8, size, EffortLevel.HEADER_CHECK)
    v_scoped = value(0.8, size, EffortLevel.SCOPED_CARVE)
    v_full = value(0.8, size, EffortLevel.FULL_CARVE)

    assert v_hdr < v_scoped < v_full

def test_budget_knapsack_allocation():
    records = [
        DeletedFileRecord(
            file_id=f"f_{i}",
            source_image="img.img",
            filesystem=Filesystem.FAT32,
            medium=Medium.HDD,
            original_name=f"file_{i}.pdf",
            size_bytes=5_000_000,
            file_category="document",
            elapsed_seconds_since_delete=100.0,
            disk_usage_pct_at_delete=0.2,
            allocation_state="entry_present"
        )
        for i in range(5)
    ]
    model = CaseAdaptiveModel()

    # Zero budget -> all SKIP
    alloc_zero = allocate_within_budget(records, model, budget_s=0.0)
    for fid, level in alloc_zero.items():
        assert level == EffortLevel.SKIP

    # Ample budget -> non-SKIP allocations
    alloc_large = allocate_within_budget(records, model, budget_s=100.0)
    non_skips = sum(1 for lvl in alloc_large.values() if lvl != EffortLevel.SKIP)
    assert non_skips > 0
