from setuptools import setup, find_packages

with open("README.md", "r") as f:
    description = f.read()

setup(
    name='fundamental_data',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        "ipykernel>=6.29.5",
        "matplotlib>=3.10.1",
        "openpyxl>=3.1.5",
        "pandas>=2.2.3",
        "requests>=2.32.3",
        "seaborn>=0.13.2",
        "yfinance>=0.2.55",
        "twine>=6.1.0"
    ],
    url='https://github.com/mashroor10/fundamental_data/tree/main',
    license='MIT',
    description='A Python package for retrieving SEC fundamental data',
    long_description=description,
    long_description_content_type="text/markdown",
    author="Mashroor Rahman",
)