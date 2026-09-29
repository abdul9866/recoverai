from common.schema import EffortLevel

# Cost estimates in seconds per MB of file size
COST_PER_MB = {
    EffortLevel.SKIP: 0.0,
    EffortLevel.HEADER_CHECK: 0.01,
    EffortLevel.SCOPED_CARVE: 0.05,
    EffortLevel.FULL_CARVE: 0.15,
}

# Yield factors per effort level (relative fraction of recoverability accessible)
YIELD_FACTOR = {
    EffortLevel.SKIP: 0.0,
    EffortLevel.HEADER_CHECK: 0.20,
    EffortLevel.SCOPED_CARVE: 0.70,
    EffortLevel.FULL_CARVE: 1.00,
}

def cost(size_bytes: int, level: EffortLevel) -> float:
    """Computes time cost in seconds for carving size_bytes at effort level."""
    mb = size_bytes / 1_048_576.0
    return max(0.001 if level != EffortLevel.SKIP else 0.0, mb * COST_PER_MB[level])

def value(expected_fraction: float, size_bytes: int, level: EffortLevel) -> float:
    """
    Computes expected recovered bytes yield at effort level:
    v(y_hat, s, e) = y_hat * s * yield_factor(e)
    """
    return expected_fraction * float(size_bytes) * YIELD_FACTOR[level]
