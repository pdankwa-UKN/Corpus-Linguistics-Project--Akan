# Corpus-Linguistics-Project--Akan

# Akan Text Processor Tool

An automated Python package built to compile, clean, segment, and analyze a linguistic corpus of Akan language text.

##Project Directory Structure
akcorp_package/ - Core Python package directory containing the backend modules.
__init__.py - Package initializer routing and function exposure.
corpli.py - Main code module containing scrapers, tokenizers, and interactive keyword search tools.
tagger.py - Custom Parts-of-Speech (POS) tagger implementation.
models/twi_pos_model.pkl - Pre-trained 82% accuracy Akan POS model file.
setup.py - Setuptools infrastructure file allowing global package installations.
MANIFEST.in - Tracks non-Python binary files (.pkl) to ensure safe package bundling.
requirements.txt - Dependency tracker registering required downstream libraries.
LICENSE - Open-source MIT distribution compliance file.

##Installation Instructions
To install this system locally as a reusable package, navigate to the root directory in your terminal and execute:
bash
pip install -e .

Dependencies handled automatically include: requests, beautifulsoup4, trafilatura, lxml_html_clean, and regex.

##Usage Guide
Open any Python environment or notebook shell and load your tools:

```python
import akcorp_package
```
url = "https://jw.org"

# 1. Scrape raw contents and extract metadata to JSON

# 2. Segment sentences and run word tokenization
akcorp_package.segment_and_tokenize_verses("final_verses.json", "final_verses.txt")

# 3. Enter interactive query  mode
corpus_analysis
corpus search
comprehensive_analysis
