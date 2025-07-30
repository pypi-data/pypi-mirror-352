from setuptools import setup, find_packages

setup(
    name="richerator",
    version="0.0.6",
    packages=find_packages(),
    install_requires=[
        "rich",
    ],
    long_description="Rich tqdm-like progress bar that hacks the print function to print in a live updating rich panel.",
)
