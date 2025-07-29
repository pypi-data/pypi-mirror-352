from setuptools import setup, find_packages

setup(
    name='automl_ai',
    version='0.1.4',
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "seaborn",
        "matplotlib",
        "scikit-learn",
        "ucimlrepo"
    ],
)
