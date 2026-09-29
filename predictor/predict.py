from predictor.model import CaseAdaptiveModel

def new_case_model() -> CaseAdaptiveModel:
    """Call this once per investigation case / disk image to instantiate adaptive predictor."""
    return CaseAdaptiveModel()
