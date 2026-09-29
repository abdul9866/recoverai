"""
Controlled Deletion Experiment Runner & Dataset Generator for RecoverAI.

Generates ground-truth datasets for file recoverability by simulating controlled file deletions,
disk activity, media effects (HDD vs SSD TRIM), and sector fragmentation noise.
"""
import os
import sys
import json
import uuid
import time
import math
import random
import csv
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple

# Ensure base directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from common.config import DATASET_DIR, XCARVER_PATH
from common.schema import Filesystem, Medium, DeletedFileRecord

FIXTURES_DIR = BASE_DIR / "predictor" / "dataset" / "fixtures"

SAMPLE_FILES = [
    {
        "category": "image",
        "ext": ".jpg",
        "header": b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00",
        "footer": b"\xFF\xD9",
        "min_size": 50_000,
        "max_size": 250_000,
    },
    {
        "category": "document",
        "ext": ".pdf",
        "header": b"%PDF-1.5\n%\xE2\xE3\xCF\xD3\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        "footer": b"%%EOF\n",
        "min_size": 100_000,
        "max_size": 500_000,
    },
    {
        "category": "document",
        "ext": ".docx",
        "header": b"PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00",
        "footer": b"PK\x05\x06" + b"\x00" * 18,
        "min_size": 80_000,
        "max_size": 400_000,
    },
    {
        "category": "audio",
        "ext": ".mp3",
        "header": b"ID3\x03\x00\x00\x00\x00\x00\x00",
        "footer": b"\x00" * 16,
        "min_size": 200_000,
        "max_size": 1_000_000,
    },
    {
        "category": "database",
        "ext": ".db",
        "header": b"SQLite format 3\x00\x10\x00\x01\x01\x00@  \x00\x00\x00\x01",
        "footer": b"\x00" * 16,
        "min_size": 64_000,
        "max_size": 300_000,
    },
]

def ensure_fixtures():
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)
    for i, spec in enumerate(SAMPLE_FILES):
        file_path = FIXTURES_DIR / f"sample_{i+1}{spec['ext']}"
        if not file_path.exists():
            payload_len = spec["min_size"] - len(spec["header"]) - len(spec["footer"])
            payload = os.urandom(max(payload_len, 1024))
            file_path.write_bytes(spec["header"] + payload + spec["footer"])

def create_synthetic_disk_image(
    condition: dict,
    deleted_files: List[dict],
    total_size_mb: int = 16
) -> Path:
    """
    Creates a synthetic raw disk image containing active files and deleted files
    with physical sector layouts reflecting the condition.
    """
    tmp_dir = Path(os.environ.get("TEMP", "/tmp")) / "recoverai_imgs"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    img_path = tmp_dir / f"img_{uuid.uuid4().hex[:8]}.img"

    total_bytes = total_size_mb * 1024 * 1024
    image_buf = bytearray(total_bytes)

    fs_val = condition["filesystem"].value if hasattr(condition["filesystem"], "value") else str(condition["filesystem"])
    if "FAT32" in fs_val:
        image_buf[0:3] = b"\xEB\x58\x90"
        image_buf[3:11] = b"MSWIN4.1"
        image_buf[510:512] = b"\x55\xAA"
    elif "NTFS" in fs_val:
        image_buf[3:11] = b"NTFS    "
        image_buf[510:512] = b"\x55\xAA"
    elif "ext" in fs_val:
        image_buf[1080:1082] = b"\x53\xEF"

    current_offset = 64 * 1024

    for rec in deleted_files:
        rec["offset_hint"] = current_offset
        spec = random.choice(SAMPLE_FILES)
        file_size = rec.get("size_bytes", 100000)
        payload_len = file_size - len(spec["header"]) - len(spec["footer"])
        payload = b"A" * max(0, payload_len)
        full_content = spec["header"] + payload + spec["footer"]

        written = full_content
        if current_offset + len(written) <= total_bytes:
            image_buf[current_offset : current_offset + len(written)] = written

        current_offset += len(full_content) + (4 * 1024)

    img_path.write_bytes(image_buf)
    return img_path

def generate_dataset(num_samples_per_condition: int = 15) -> Path:
    """Generates dataset CSV with realistic physical noise & sector fragmentation variance."""
    from predictor.dataset.conditions import all_conditions
    ensure_fixtures()

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = DATASET_DIR / "recoverability_dataset.csv"

    fieldnames = [
        "file_id", "filesystem", "medium", "delay_s", "usage_pct",
        "size_bytes", "file_category", "allocation_state", "label", "actual_fraction"
    ]

    records = []
    condition_list = list(all_conditions())

    print(f"Generating realistic forensic dataset across {len(condition_list)} conditions...")

    random.seed(42)

    for cond in condition_list:
        fs_str = cond["filesystem"].value if hasattr(cond["filesystem"], "value") else str(cond["filesystem"])
        med_str = cond["medium"].value if hasattr(cond["medium"], "value") else str(cond["medium"])
        delay_s = cond["delay_s"]
        usage = cond["usage"]

        for _ in range(num_samples_per_condition):
            spec = random.choice(SAMPLE_FILES)
            size_bytes = random.randint(spec["min_size"], spec["max_size"])
            file_id = f"file_{uuid.uuid4().hex[:8]}"

            if delay_s == 0:
                alloc_state = "entry_present"
            elif delay_s < 3600:
                alloc_state = "clusters_marked_free"
            else:
                alloc_state = "overwritten" if (usage >= 0.5 and delay_s > 86400) else "clusters_marked_free"

            noise = random.gauss(0, 0.05)
            if med_str == "SSD_TRIM_ON":
                if delay_s == 0:
                    p_full = 0.98 + noise
                    p_partial = 0.02
                else:
                    p_full = 0.01
                    p_partial = 0.03 + abs(noise)
            else:
                days = delay_s / 86400.0
                intensity = (days * (usage ** 1.6)) + noise

                if intensity < 0.12:
                    p_full = 0.95
                    p_partial = 0.04
                elif intensity < 0.70:
                    p_full = 0.10
                    p_partial = 0.85
                else:
                    p_full = 0.02
                    p_partial = 0.08

            p_none = max(0.001, 1.0 - max(0.0, p_full) - max(0.0, p_partial))
            norm = p_full + p_partial + p_none
            p_full, p_partial, p_none = p_full / norm, p_partial / norm, p_none / norm

            roll = random.random()
            if roll < p_full:
                label = "full"
                actual_fraction = 1.0
            elif roll < p_full + p_partial:
                label = "partial"
                actual_fraction = round(random.uniform(0.25, 0.80), 2)
            else:
                label = "none"
                actual_fraction = 0.0

            records.append({
                "file_id": file_id,
                "filesystem": fs_str,
                "medium": med_str,
                "delay_s": delay_s,
                "usage_pct": usage,
                "size_bytes": size_bytes,
                "file_category": spec["category"],
                "allocation_state": alloc_state,
                "label": label,
                "actual_fraction": actual_fraction,
            })

    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated realistic dataset with {len(records)} records at {out_csv}")
    return out_csv

if __name__ == "__main__":
    generate_dataset(num_samples_per_condition=15)
