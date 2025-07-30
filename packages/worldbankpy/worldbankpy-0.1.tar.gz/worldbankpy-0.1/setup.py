from setuptools import setup, find_packages

setup(
    name="worldbankpy",
    version="0.1",
    packages=find_packages(),
    description="Fetches macroeconomic data from World Bank.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="nndjoli",
    url="https://github.com/nndjoli/world-bank-data-fetcher",
    requires=["requests", "pandas", "datetime"],
)
