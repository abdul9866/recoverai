from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class Filesystem(str, Enum):
    FAT32 = "FAT32"
    EXFAT = "exFAT"
    NTFS = "NTFS"
    EXT4 = "ext4"
    F2FS = "F2FS"
    HFS_PLUS = "HFS+"
    APFS = "APFS"
    BTRFS = "Btrfs"
    YAFFS2 = "YAFFS2"

class Medium(str, Enum):
    HDD = "HDD"
    SSD_TRIM_ON = "SSD_TRIM_ON"
    SSD_TRIM_OFF = "SSD_TRIM_OFF"

class EffortLevel(str, Enum):
    SKIP = "skip"
    HEADER_CHECK = "header_check"
    SCOPED_CARVE = "scoped_carve"
    FULL_CARVE = "full_carve"

@dataclass
class DeletedFileRecord:
    file_id: str
    source_image: str
    filesystem: Filesystem
    medium: Medium
    original_name: Optional[str]
    size_bytes: int
    file_category: str          # matches xCarver's signature categories
    elapsed_seconds_since_delete: float
    disk_usage_pct_at_delete: float
    allocation_state: str       # "entry_present" | "clusters_marked_free" | "overwritten"
    offset_hint: Optional[int] = None   # byte offset if known from FS metadata

@dataclass
class RecoverabilityPrediction:
    file_id: str
    p_full: float
    p_partial: float
    expected_fraction: float
    confidence: float

@dataclass
class RecoveryResult:
    file_id: str
    effort_used: EffortLevel
    bytes_recovered: int
    bytes_expected: int
    success: bool
    time_taken_s: float

@dataclass
class SearchHit:
    file_id: str
    path: str
    similarity: float
    recovery_confidence: float
    completeness_fraction: float
    fused_score: float
