from setuptools import setup, find_packages

setup(
    name="akcorp_package",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests", "beautifulsoup4", "trafilatura", "lxml_html_clean","regex"],)
