from setuptools import setup, find_packages

setup(
    name="pain-imputer",
    version="0.1.0",
    author="Rajeshwari Mistri",
    author_email="rajeshwarimistri11@gmail.com",
    description="PAIN : A library for imputing missing values",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pain-imputer",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn",
        "tensorflow==2.12.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    include_package_data=True,
    python_requires=">=3.7",

    keywords="data-imputation missing-data machine-learning scikit-learn random-forest autoencoder mixed-dataset",
    project_urls={
        "Bug Tracker": "https://github.com/parulkumari2707/FRAME-FEATURE-SELECTOR/issues",
        "Documentation": "https://github.com/parulkumari2707/FRAME-FEATURE-SELECTOR#readme"
    }
)