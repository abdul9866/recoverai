import numpy as np
from common.schema import DeletedFileRecord

FS_ENCODING = {
    "FAT32": 0, "exFAT": 1, "NTFS": 2, "ext4": 3, "F2FS": 4,
    "HFS+": 5, "APFS": 6, "Btrfs": 7, "YAFFS2": 8
}
MEDIUM_ENCODING = {"HDD": 0, "SSD_TRIM_ON": 1, "SSD_TRIM_OFF": 2}
ALLOC_ENCODING = {"entry_present": 0, "clusters_marked_free": 1, "overwritten": 2}
CAT_ENCODING = {"image": 0, "document": 1, "audio": 2, "database": 3, "executable": 4, "misc": 5}

FEATURE_NAMES = [
    "filesystem", "medium", "log_elapsed_s", "disk_usage_pct",
    "log_size_bytes", "allocation_state", "category",
    "medium_x_delay", "usage_x_delay", "size_x_usage",
    "is_ssd_trim", "delay_sq", "usage_sq"
]

def to_feature_vector(rec: DeletedFileRecord) -> np.ndarray:
    fs_val = rec.filesystem.value if hasattr(rec.filesystem, "value") else str(rec.filesystem)
    med_val = rec.medium.value if hasattr(rec.medium, "value") else str(rec.medium)
    alloc_val = str(rec.allocation_state)
    cat_val = str(rec.file_category).lower()

    med_num = MEDIUM_ENCODING.get(med_val, 0)
    delay_log = np.log1p(max(0.0, float(rec.elapsed_seconds_since_delete)))
    usage_pct = float(rec.disk_usage_pct_at_delete)
    size_log = np.log1p(max(0.0, float(rec.size_bytes)))
    is_trim = 1.0 if med_val == "SSD_TRIM_ON" else 0.0

    return np.array([
        FS_ENCODING.get(fs_val, 0),
        med_num,
        delay_log,
        usage_pct,
        size_log,
        ALLOC_ENCODING.get(alloc_val, 1),
        CAT_ENCODING.get(cat_val, 1),
        med_num * delay_log,
        usage_pct * delay_log,
        size_log * usage_pct,
        is_trim,
        delay_log ** 2,
        usage_pct ** 2
    ], dtype=float)

def dict_to_feature_vector(d: dict) -> np.ndarray:
    fs_val = str(d.get("filesystem", "FAT32"))
    med_val = str(d.get("medium", "HDD"))
    alloc_val = str(d.get("allocation_state", "clusters_marked_free"))
    cat_val = str(d.get("file_category", "document")).lower()

    med_num = MEDIUM_ENCODING.get(med_val, 0)
    delay_log = np.log1p(max(0.0, float(d.get("delay_s", 0))))
    usage_pct = float(d.get("usage_pct", 0.5))
    size_log = np.log1p(max(0.0, float(d.get("size_bytes", 100000))))
    is_trim = 1.0 if med_val == "SSD_TRIM_ON" else 0.0

    return np.array([
        FS_ENCODING.get(fs_val, 0),
        med_num,
        delay_log,
        usage_pct,
        size_log,
        ALLOC_ENCODING.get(alloc_val, 1),
        CAT_ENCODING.get(cat_val, 1),
        med_num * delay_log,
        usage_pct * delay_log,
        size_log * usage_pct,
        is_trim,
        delay_log ** 2,
        usage_pct ** 2
    ], dtype=float)
