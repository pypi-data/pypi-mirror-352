from setuptools import setup, find_packages

setup(
    name="mvcluster",
    version="1.12",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "scikit-learn",
        "torch",
        "scipy",
    ],
    test_suite="tests",
)
