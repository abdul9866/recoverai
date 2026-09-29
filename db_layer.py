#!/usr/bin/env python3
"""
RecoverAI v2.0 – SQLite Database Layer
Replaces flat CSV exports with a structured SQLite database via SQLAlchemy.
Tables: experiments, manifest, verdicts, predictions, search_index, allocations
"""

import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Boolean, Text,
    DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DB_PATH = os.environ.get("DB_PATH", "./db/recoverai.db")
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# ─────────────────────────── ORM Models ──────────────────────────────────────

class Experiment(Base):
    __tablename__ = "experiments"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    run_id          = Column(String(64), unique=True, nullable=False)
    started_at      = Column(DateTime, default=datetime.utcnow)
    finished_at     = Column(DateTime, nullable=True)
    git_commit      = Column(String(40), nullable=True)
    python_version  = Column(String(20))
    notes           = Column(Text, nullable=True)
    filesystems     = Column(String(128))   # JSON-encoded list
    conditions_count= Column(Integer)
    verdicts        = relationship("Verdict", back_populates="experiment")
    predictions     = relationship("Prediction", back_populates="experiment")


class FileManifest(Base):
    __tablename__ = "manifest"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    file_name       = Column(String(256), nullable=False)
    file_type       = Column(String(16))
    size_bytes      = Column(Integer)
    total_4kb_blocks= Column(Integer)
    sha256          = Column(String(64), unique=True)
    block_hashes_json = Column(Text)
    created_at      = Column(DateTime, default=datetime.utcnow)


class Verdict(Base):
    __tablename__ = "verdicts"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    experiment_run  = Column(String(64), ForeignKey("experiments.run_id"))
    condition_id    = Column(String(16))
    filesystem      = Column(String(16))
    discard         = Column(Boolean)
    filler_mb       = Column(Integer)
    occupancy       = Column(String(8))
    file_name       = Column(String(256))
    file_type       = Column(String(16))
    size_bytes      = Column(Integer)
    verdict         = Column(String(64))           # "FULL" | "PARTIAL" | "NOT_RETRIEVED"
    recovered_fraction = Column(Float)
    sha256_match    = Column(Boolean)
    recovery_time_s = Column(Float)
    experiment      = relationship("Experiment", back_populates="verdicts")


class Prediction(Base):
    __tablename__ = "predictions"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    experiment_run  = Column(String(64), ForeignKey("experiments.run_id"))
    condition_id    = Column(String(16))
    file_name       = Column(String(256))
    p_none          = Column(Float)
    p_partial       = Column(Float)
    p_full          = Column(Float)
    predicted_expected_fraction = Column(Float)
    predicted_class = Column(String(16))
    actual_verdict  = Column(String(64))
    correct         = Column(Boolean)
    model_type      = Column(String(32))    # "xgboost" | "pytorch_nn"
    experiment      = relationship("Experiment", back_populates="predictions")


class SearchIndex(Base):
    __tablename__ = "search_index"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    experiment_run  = Column(String(64))
    doc_id          = Column(String(128), unique=True)
    file_name       = Column(String(256))
    condition_id    = Column(String(16))
    verdict         = Column(String(64))
    confidence      = Column(Float)
    completeness    = Column(Float)
    text_snippet    = Column(Text)
    indexed_at      = Column(DateTime, default=datetime.utcnow)


class AllocationRecord(Base):
    __tablename__ = "allocations"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    experiment_run  = Column(String(64))
    condition_id    = Column(String(16))
    file_name       = Column(String(256))
    predicted_fraction = Column(Float)
    allocated_effort= Column(String(32))
    allocated_time_s= Column(Float)
    actual_verdict  = Column(String(64))


class MLMetrics(Base):
    __tablename__ = "ml_metrics"
    id              = Column(Integer, primary_key=True, autoincrement=True)
    experiment_run  = Column(String(64))
    model_type      = Column(String(32))
    accuracy        = Column(Float)
    f1_weighted     = Column(Float)
    roc_auc_ovr     = Column(Float, nullable=True)
    mae             = Column(Float)
    rmse            = Column(Float)
    r2              = Column(Float)
    frr             = Column(Float)    # False Retirement Rate
    precision_at_1  = Column(Float)
    precision_at_3  = Column(Float)
    recorded_at     = Column(DateTime, default=datetime.utcnow)


# ─────────────────────────── Public API ──────────────────────────────────────

def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(engine)
    print(f"[DB] SQLite database initialised at: {DB_PATH}")


def save_manifest(manifest_rows: list[dict]):
    """Upsert file manifest rows."""
    session = Session()
    try:
        for row in manifest_rows:
            existing = session.query(FileManifest).filter_by(sha256=row["sha256"]).first()
            if existing:
                continue
            session.add(FileManifest(
                file_name=row["file"],
                file_type=row["type"],
                size_bytes=row["size_bytes"],
                total_4kb_blocks=row["total_4kb_blocks"],
                sha256=row["sha256"],
                block_hashes_json=row["block_hashes_json"]
            ))
        session.commit()
        print(f"[DB] Saved {len(manifest_rows)} manifest records.")
    finally:
        session.close()


def create_experiment(run_id: str, git_commit: str, filesystems: list, conditions_count: int, notes: str = "") -> str:
    """Register a new experiment run."""
    import sys
    session = Session()
    try:
        exp = Experiment(
            run_id=run_id,
            git_commit=git_commit,
            python_version=sys.version[:16],
            notes=notes,
            filesystems=json.dumps(filesystems),
            conditions_count=conditions_count
        )
        session.add(exp)
        session.commit()
        print(f"[DB] Created experiment run: {run_id}")
        return run_id
    finally:
        session.close()


def save_verdicts(run_id: str, verdict_rows: list[dict]):
    session = Session()
    try:
        for row in verdict_rows:
            session.add(Verdict(
                experiment_run=run_id,
                condition_id=row["condition_id"],
                filesystem=row["filesystem"],
                discard=bool(row["discard"]),
                filler_mb=int(row["filler_MB"]),
                occupancy=row["occupancy"],
                file_name=row["file"],
                file_type=row["type"],
                size_bytes=int(row["size"]),
                verdict=row["verdict"],
                recovered_fraction=float(row["recovered_fraction"]),
                sha256_match=bool(row["sha256_match"]),
                recovery_time_s=float(row["recovery_time_s"])
            ))
        session.commit()
        print(f"[DB] Saved {len(verdict_rows)} verdict records.")
    finally:
        session.close()


def save_predictions(run_id: str, prediction_rows: list[dict], model_type: str = "pytorch_nn"):
    session = Session()
    try:
        for row in prediction_rows:
            session.add(Prediction(
                experiment_run=run_id,
                condition_id=row["condition_id"],
                file_name=row["file"],
                p_none=float(row.get("p_none", 0.0)),
                p_partial=float(row.get("p_partial", 0.0)),
                p_full=float(row.get("p_full", 0.0)),
                predicted_expected_fraction=float(row.get("predicted_expected_fraction", 0.0)),
                predicted_class=row.get("predicted_class", "none"),
                actual_verdict=row.get("verdict", ""),
                correct=bool(row.get("correct", False)),
                model_type=model_type
            ))
        session.commit()
        print(f"[DB] Saved {len(prediction_rows)} prediction records.")
    finally:
        session.close()


def save_allocations(run_id: str, alloc_rows: list[dict]):
    session = Session()
    try:
        for row in alloc_rows:
            session.add(AllocationRecord(
                experiment_run=run_id,
                condition_id=row["condition_id"],
                file_name=row["file"],
                predicted_fraction=float(row["predicted_expected_fraction"]),
                allocated_effort=row["allocated_effort"],
                allocated_time_s=float(row["allocated_time_s"]),
                actual_verdict=row["actual_verdict"]
            ))
        session.commit()
        print(f"[DB] Saved {len(alloc_rows)} allocation records.")
    finally:
        session.close()


def save_search_index_record(run_id: str, doc_id: str, file_name: str,
                              condition_id: str, verdict: str, confidence: float,
                              completeness: float, snippet: str):
    session = Session()
    try:
        existing = session.query(SearchIndex).filter_by(doc_id=doc_id).first()
        if not existing:
            session.add(SearchIndex(
                experiment_run=run_id,
                doc_id=doc_id,
                file_name=file_name,
                condition_id=condition_id,
                verdict=verdict,
                confidence=confidence,
                completeness=completeness,
                text_snippet=snippet[:512]
            ))
            session.commit()
    finally:
        session.close()


def save_ml_metrics(run_id: str, model_type: str, metrics: dict):
    session = Session()
    try:
        session.add(MLMetrics(
            experiment_run=run_id,
            model_type=model_type,
            accuracy=metrics.get("accuracy", 0.0),
            f1_weighted=metrics.get("f1_weighted", 0.0),
            roc_auc_ovr=metrics.get("roc_auc_ovr"),
            mae=metrics.get("mae", 0.0),
            rmse=metrics.get("rmse", 0.0),
            r2=metrics.get("r2", 0.0),
            frr=metrics.get("frr", 0.0),
            precision_at_1=metrics.get("precision_at_1", 0.0),
            precision_at_3=metrics.get("precision_at_3", 0.0)
        ))
        session.commit()
        print(f"[DB] Saved ML metrics for model: {model_type}")
    finally:
        session.close()


def finish_experiment(run_id: str):
    session = Session()
    try:
        exp = session.query(Experiment).filter_by(run_id=run_id).first()
        if exp:
            exp.finished_at = datetime.utcnow()
            session.commit()
            print(f"[DB] Marked experiment {run_id} as finished.")
    finally:
        session.close()


def query_all_verdicts(run_id: str) -> list:
    session = Session()
    try:
        rows = session.query(Verdict).filter_by(experiment_run=run_id).all()
        return [
            {
                "condition_id": r.condition_id,
                "filesystem": r.filesystem,
                "discard": r.discard,
                "filler_MB": r.filler_mb,
                "occupancy": r.occupancy,
                "file": r.file_name,
                "type": r.file_type,
                "size": r.size_bytes,
                "verdict": r.verdict,
                "recovered_fraction": r.recovered_fraction,
                "sha256_match": r.sha256_match,
                "recovery_time_s": r.recovery_time_s
            }
            for r in rows
        ]
    finally:
        session.close()


def print_db_summary(run_id: str):
    """Print row counts for each table for this run."""
    session = Session()
    try:
        n_verdicts  = session.query(Verdict).filter_by(experiment_run=run_id).count()
        n_preds     = session.query(Prediction).filter_by(experiment_run=run_id).count()
        n_allocs    = session.query(AllocationRecord).filter_by(experiment_run=run_id).count()
        n_search    = session.query(SearchIndex).filter_by(experiment_run=run_id).count()
        n_metrics   = session.query(MLMetrics).filter_by(experiment_run=run_id).count()
        n_manifest  = session.query(FileManifest).count()

        print("\n╔══════════════════════════════════════════════╗")
        print("║         SQLite Database Summary              ║")
        print("╠══════════════════════════════════════════════╣")
        print(f"║  File Manifest records  : {n_manifest:6d}            ║")
        print(f"║  Verdict records        : {n_verdicts:6d}            ║")
        print(f"║  Prediction records     : {n_preds:6d}            ║")
        print(f"║  Allocation records     : {n_allocs:6d}            ║")
        print(f"║  Search Index entries   : {n_search:6d}            ║")
        print(f"║  ML Metric snapshots    : {n_metrics:6d}            ║")
        print("╚══════════════════════════════════════════════╝")
    finally:
        session.close()
