"""Package installer"""

from setuptools import find_packages, setup  # type: ignore

setup(
    name="homework",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "scikit-learn",
        "seaborn",
        "matplotlib",
        "lightgbm",
        "laspy",
        "plotly",
        "rasterio",
    ],
)
