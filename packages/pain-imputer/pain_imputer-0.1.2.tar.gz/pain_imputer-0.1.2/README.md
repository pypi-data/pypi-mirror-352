# PAIN-Imputer: Precision Adaptive Imputation for Mixed-Type Data

[![PyPI version](https://badge.fury.io/py/pain-imputer.svg)](https://pypi.org/project/pain-imputer/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Build Status](https://github.com/RajEshwariCodes/pain-imputer/actions/workflows/ci.yml/badge.svg)](https://github.com/RajEshwariCodes/pain-imputer/actions)


>`pain-imputer` is a Python package built around the values and research-backed **Precision Adaptive Imputation Network (PAIN)** a tri-step imputation framework designed to handle datasets containing both **numerical and categorical features** with varying missingness patterns.

---

## Table of Contents
- [What is PAIN?](#what-is-PAIN)
- [Key Features](#key-features)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [API Reference](#api-reference)
- [How It Works](#how-it-works)
- [Use Cases](#use-cases)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## What is PAIN?

PAIN Imputer is a state-of-the-art missing data imputation library that combines statistical methods, machine learning, and neural networks in a tri-step architecture. It is a research-based architecture, proposed in [PAIN paper on arXiv] (https://arxiv.org/abs/2501.10667) consistently outperforms traditional imputation methods while preserving data distributions and relationships.

Unlike traditional imputers that rely on statistical or machine learning methods, PAIN-Imputer combines **three complementary strategies**:
1. **Statistical Imputation**
2. **Machine Learning-based Estimation**
3. **Neural Autoencoder with Iterative Refinement**

**Note**: This is a beta release; expect updates as we continue to refine the library.

# Key Features
- Handles both categorical and numerical data
- Tri-step imputation strategy for high accuracy and stability
- Works well with high-dimensional datasets
- Automatically detects data types and missingness patterns
- Research-validated on real-world benchmark datasets
- Easy to integrate into any ML pipeline

---

# Installation

- Install from PyPI:
```bash
pip install pain-imputer
```
Or

- Install from source:
```bash
git clone https://github.com/RajEshwariCodes/PAIN_Library.git
cd pain-imputer
pip install -e .
```

# Requirements
- Python ≥ 3.7
- numpy 
- pandas 
- scikit-learn 
- tensorflow 

# Quickstart
``` python
import pandas as pd
import numpy as np
from pain_imputer import PAINImputer

# Load your data with missing values
data = pd.read_csv('your_dataset.csv')

# Initialize PAIN Imputer
imputer = PAINImputer(
    n_iterations=5,
    n_neighbors=5,
    random_state=42
)

# Transform incomplete data to complete
imputed_data = imputer.fit_transform(data)

print(f"Missing values before: {data.isnull().sum().sum()}")
print(f"Missing values after: {imputed_data.isnull().sum().sum()}")
```
## Real-World Example: Forest Fire Data

``` python
import pandas as pd
from pain_imputer import PAINImputer

#Load forest fire dataset with missing values
df = pd.read_csv('forestfires.csv')

#Create PAIN imputer with custom settings
imputer = PAINImputer(
    n_iterations=3,          # Number of refinement iterations
    n_neighbors=7,           # KNN neighbors for baseline
    n_estimators=150,        # Random Forest trees
    encoder_layers=[128, 64, 32],  # Autoencoder architecture
    random_state=42
)

#Impute missing values
complete_data = imputer.fit_transform(df)

#Verify data integrity
print("Original data shape:", df.shape)
print("Imputed data shape:", complete_data.shape)
print("Data types preserved:", (df.dtypes == complete_data.dtypes).all())
```

---

# API Reference
``` python
PAINImputer Class
class PAINImputer:
    def __init__(
        self,
        n_iterations: int = 5,
        n_neighbors: int = 5,
        n_estimators: int = 100,
        encoder_layers: List[int] = [64, 32, 16],
        random_state: int = 42
    )

```

## Parameters
| Parameter           | Type      | Default      | Description                                |
|---------------------|-----------|--------------|--------------------------------------------|
| n_iterations        | int       | 5            | Number of refinement iterations in Layer 2 |
| n_neighbors         | int       | 5            | Number of neighbors for KNN imputation     |
| n_estimators        | int       | 100          | Number of trees in Random Forest           |
| encoder_layers      | List[int] | [64, 32, 16] | Hidden layer sizes for autoencoder         |
| random_state        | int       | 42           | Random seed for reproducibility            |

---

# Running Tests
To run the test suite and verify the library’s functionality, use **pytest**. First, ensure you have **pytest** installed:
```bash
pip install pytest
```
Then, run the tests:
```bash
pytest tests/
```
This will execute all unit tests in the **tests/** directory, helping contributors ensure their changes don’t break existing functionality.

---

# How It Works 
(Tri-Step Pipeline)
- **Baseline Imputation**  
  Uses mean/median/KNN weighted by missingness ratio.
- **Advanced Modeling**  
  Uses random forests and autoencoders to refine imputations iteratively.
- **Refinement**
  Clips imputed values to avoid outliers, preserving statistical consistency.

---

# Use Cases
- Medical datasets with missing physiological values
- Mixed survey data (text + numbers)
- High-dimensional research datasets
- ML preprocessing pipelines
- Any situation where missing values exist in structured data

---

# Contributing
We welcome contributions ! Whether it’s a bug fix, feature request, or new idea, submit pull requests via our GitHub repository.

# License
This project is licensed under the MIT License - see the LICENSE file for details.

# Contact
Maintainer: Rajeshwari Mistri
Email: [rajeshwarimistri11@gmail.com] (mailto:rajeshwarimistri11@gmail.com)
Project Repository: [GitHub](https://github.com/RajEshwariCodes/PAIN_Library)

## **Ready to make missing data painless?** pip install pain-imputer and transform your incomplete datasets today! 