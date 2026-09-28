from setuptools import setup, find_packages

setup(
    name="quant_pipeline",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "scikit-learn",
        "plotly",
        "pyarrow",
        "statsmodels",
    ],
    entry_points={
        "console_scripts": [
            "quant-pipeline=quant_pipeline.cli:main",
        ],
    },
)
