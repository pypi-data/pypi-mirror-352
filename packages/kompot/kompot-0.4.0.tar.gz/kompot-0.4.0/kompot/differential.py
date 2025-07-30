"""
Differential analysis module for Kompot (for backward compatibility).

This module re-exports classes from the differential submodule.
New code should import directly from kompot.differential instead.
"""

from kompot.differential.differential_abundance import DifferentialAbundance
from kompot.differential.differential_expression import DifferentialExpression
from kompot.differential.sample_variance_estimator import SampleVarianceEstimator
from kompot.differential.utils import compute_weighted_mean_fold_change

__all__ = [
    "DifferentialAbundance",
    "DifferentialExpression",
    "SampleVarianceEstimator",
    "compute_weighted_mean_fold_change"
]