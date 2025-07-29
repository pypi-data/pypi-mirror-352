import io
import os
from setuptools import setup, find_packages

# Read long description from README.md
here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hygiea",
    version="0.5.1",
    author="Ejiga Peter Ojonugwa",
    author_email="ejigsonpeter@gmail.com",
    description="Comprehensive Data Cleaning, Profiling, and EDA Toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ejigsonpeter/hygiea",
    license_expression="MIT",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "pandas>=1.0.0",
        "PyJWT>=1.0.0",
        "numpy>=1.18.0",
        "pyyaml>=5.1",
        "scikit-learn",
        "pandas_profiling>=3.0.0",
        "matplotlib>=3.0.0",
        "seaborn>=0.10.0",
        "sqlalchemy>=1.3.0",
        "nltk>=3.5",
        "spacy>=3.0.0",
        "xgboost>=1.3.0",
        "scipy>=1.4.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "hygiea = hygiea.cli:main",
        ],
        "hygiea.plugins": []
    },
)
