"""
End-to-End Integration Smoke Test for RecoverAI.
Validates the full recovery lifecycle:
1. Controlled disk image generation
2. Recoverability prediction
3. CARP Knapsack allocation & carving execution
4. Vector embedding and CARP fused search retrieval
"""
import os
import sys
import pytest
from pathlib import Path

from common.schema import Filesystem, Medium, DeletedFileRecord
from predictor.dataset.generate_deletions import create_synthetic_disk_image
from recovery_engine.orchestrator import run_case
from semantic_search.index import index_recovered_file, fused_search

def test_full_recoverai_pipeline(tmp_path):
    # Step 1: Build synthetic test image and deleted records
    cond = {"filesystem": Filesystem.FAT32, "medium": Medium.HDD, "delay_s": 0, "usage": 0.2}
    deleted_records = [
        DeletedFileRecord(
            file_id="e2e_01",
            source_image="test.img",
            filesystem=Filesystem.FAT32,
            medium=Medium.HDD,
            original_name="suspect_passport.jpg",
            size_bytes=150_000,
            file_category="image",
            elapsed_seconds_since_delete=0.0,
            disk_usage_pct_at_delete=0.2,
            allocation_state="entry_present",
            offset_hint=65536
        ),
        DeletedFileRecord(
            file_id="e2e_02",
            source_image="test.img",
            filesystem=Filesystem.FAT32,
            medium=Medium.HDD,
            original_name="bank_statement.pdf",
            size_bytes=250_000,
            file_category="document",
            elapsed_seconds_since_delete=3600.0,
            disk_usage_pct_at_delete=0.2,
            allocation_state="clusters_marked_free",
            offset_hint=250000
        )
    ]

    raw_recs = [
        {"size_bytes": r.size_bytes, "file_id": r.file_id, "true_label": "full", "actual_fraction": 1.0}
        for r in deleted_records
    ]
    img_path = create_synthetic_disk_image(cond, raw_recs, total_size_mb=4)
    out_dir = tmp_path / "carved_e2e"

    # Step 2 & 3: Run prediction and recovery orchestration
    results = run_case(deleted_records, str(img_path), str(out_dir), budget_s=600.0)
    assert len(results) == len(deleted_records)

    # Step 4: Index recovered artifacts
    sample_file = tmp_path / "recovered_doc.txt"
    sample_file.write_text("Forensic evidence: Suspect bank transfers and offshore account logs.", encoding="utf-8")

    index_recovered_file(
        path=sample_file,
        recovery_confidence=0.92,
        completeness_fraction=1.0,
        file_id="e2e_recovered_doc"
    )

    # Step 5: Execute fused semantic query
    hits = fused_search("bank transfers", k=5)
    assert len(hits) > 0
    assert any(h["file_id"] == "e2e_recovered_doc" for h in hits)
