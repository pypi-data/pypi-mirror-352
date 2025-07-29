"""
PAIN-Imputer Library Initialization
-----------------------------------

This package provides the PAINImputer class for advanced data imputation using
a tri-step hybrid approach:
1. Statistical Imputation
2. Machine Learning-based Estimation
3. Neural Autoencoder with Iterative Refinement

PAIN (Precision Adaptive Imputation Network) is designed to handle real-world datasets
with mixed feature types and complex missingness patterns.

Usage:
    from .imputer import PAINImputer
"""
from .imputer import PAINImputer