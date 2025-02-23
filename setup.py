from setuptools import setup, find_packages

setup(
    name="data-analysis",              
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # Basic minimal example; see below for alternative ways
        "pandas",
        "numpy",
        "scikit-learn",
        "sqlalchemy",
        "statsmodels",
        # ...
    ],
)
