"""
AirVision AI — ML Pipeline Wrapper (backend side)
=================================================
Makes the trained prediction object (models/model.pkl) importable from the
Flask backend. The pipeline class lives in ml/pipeline.py; unpickling needs
that module importable, so we add the ml/ directory to sys.path here.
"""

import os
import sys

from config import Config

# Ensure ml/ is importable so pickle can find the PredictionPipeline class
_ML_DIR = os.path.join(Config.PROJECT_ROOT, "ml")
if _ML_DIR not in sys.path:
    sys.path.insert(0, _ML_DIR)

from pipeline import PredictionPipeline  # noqa: E402  (import after sys.path fix)


def load(path: str = None) -> PredictionPipeline:
    """Load and return the trained pipeline."""
    return PredictionPipeline.load(path or Config.MODEL_PATH)
