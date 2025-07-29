from setuptools import setup, find_packages
from pathlib import Path

about = {}
ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = ROOT_DIR / "loan_approval_model"


setup(
    name="loan_approval_model",
    version="0.0.2",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
)