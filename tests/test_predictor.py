import pytest
from common.schema import Filesystem, Medium, DeletedFileRecord
from predictor.model import CaseAdaptiveModel

def test_theta_movement_synthetic_outcomes():
    model = CaseAdaptiveModel(theta=1.0, learning_rate=0.2)
    initial_theta = model.theta
    assert initial_theta == 1.0

    # Scenario 1: Actual recovery exceeded predicted -> theta should increase
    model.update(predicted_fraction=0.4, actual_fraction=0.8)  # ratio = 2.0
    assert model.theta > initial_theta

    # Scenario 2: Actual recovery fell short -> theta should decrease
    prev_theta = model.theta
    model.update(predicted_fraction=0.8, actual_fraction=0.2)  # ratio = 0.25
    assert model.theta < prev_theta

def test_predictor_feature_conversion():
    rec = DeletedFileRecord(
        file_id="test_01",
        source_image="dummy.img",
        filesystem=Filesystem.FAT32,
        medium=Medium.HDD,
        original_name="sample.jpg",
        size_bytes=102400,
        file_category="image",
        elapsed_seconds_since_delete=3600.0,
        disk_usage_pct_at_delete=0.5,
        allocation_state="clusters_marked_free"
    )
    model = CaseAdaptiveModel()
    pred = model.predict(rec)
    assert pred.file_id == "test_01"
    assert 0.0 <= pred.expected_fraction <= 1.0
    assert 0.0 <= pred.confidence <= 1.0
