# Corpus-Linguistics-Project--Akan

# Akan Text Processor Tool

An automated Python package built to compile, clean, segment, and analyze a linguistic corpus of Akan language text.

##Project Directory Structure
akcorp_package/ - Core Python package directory containing the backend modules.
__init__.py - Package initializer routing and function exposure.
corpli.py - Main code module containing scrapers, tokenizers, and interactive keyword search tools.
setup.py - Setuptools infrastructure file allowing global package installations.
requirements.txt - Dependency tracker registering required downstream libraries.
LICENSE - Open-source MIT distribution compliance file.

##Installation Instructions
To install this system locally as a reusable package, navigate to the root directory in your terminal and execute:
bash
pip install -e .

Dependencies handled automatically include: requests, beautifulsoup4, trafilatura, lxml_html_clean, and regex.

##Usage Guide
Open any Python environment or notebook shell and load your tools cleanly:

```python
import akcorp_package
```
url = "https://jw.org"

# 1. Scrape raw contents to JSON
akcorp_package.scrape_verses_to_json(url, "final_verses.json")

# 2. Segment sentences and run word tokenization
akcorp_package.segment_and_tokenize_verses("final_verses.json", "final_verses.txt")

# 3. Enter interactive query evaluation index analysis mode
akcorp_package.corpus_analysis("final_verses.txt", "search_analysis_results.txt")
