import os
import pytest
from pathlib import Path
from semantic_search.extract import extract_text, is_image
from semantic_search.embed import embed_text, embed_query
from semantic_search.index import index_recovered_file, fused_search

def test_text_extraction(tmp_path):
    txt_file = tmp_path / "forensic_report.txt"
    txt_file.write_text("Evidence log: Deleted financial records located.", encoding="utf-8")

    text = extract_text(txt_file)
    assert "financial records" in text
    assert not is_image(txt_file)

def test_fused_search_score_ordering(tmp_path):
    f1 = tmp_path / "doc_high_conf.txt"
    f1.write_text("Confidential transaction ledger for suspect account.", encoding="utf-8")

    f2 = tmp_path / "doc_low_conf.txt"
    f2.write_text("Confidential transaction ledger for suspect account.", encoding="utf-8")

    # Index both files with identical content but different CARP confidence scores
    index_recovered_file(f1, recovery_confidence=0.95, completeness_fraction=1.0, file_id="high_conf")
    index_recovered_file(f2, recovery_confidence=0.10, completeness_fraction=0.2, file_id="low_conf")

    hits = fused_search("transaction ledger", k=2)
    assert len(hits) == 2
    # High confidence file must rank above low confidence file despite identical similarity
    assert hits[0]["file_id"] == "high_conf"
    assert hits[0]["fused_score"] > hits[1]["fused_score"]
