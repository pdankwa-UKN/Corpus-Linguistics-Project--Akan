# Corpus-Linguistics-Project--Akan

# Akan Text Processor Tool

A Python package for collecting, cleaning and analysing a small corpus of Akan text.

**##Project Structure**
akcorp_package/ -  main package.
__init__.py - Package initializer routing and function exposure.
corpli.py - Main code module containing scrapers, tokenizers, and interactive keyword search tools.
tagger.py - Custom Parts-of-Speech (POS) tagger implementation.
models/twi_pos_model.pkl - Pre-trained 82% accuracy Akan POS model file.
setup.py - Setuptools for package installation.
MANIFEST.in – includes the model file when the package is built
requirements.txt – required dependencies
LICENSE – MIT license

**##Installation Instructions**
To install the package, open a terminal in the main project folder and run:

bash
pip install -e .

Dependencies installed automatically include: requests, beautifulsoup4, trafilatura, lxml_html_clean, and regex.

**##Usage Guide**
Open any Python environment or notebook shell and import package:

```python
import akcorp_package
```
url = "https://jw.org"

** Scraping**
The scraping code collects the selected Akan Bible chapters from jw.org. The raw text is saved in scraped_verses.json and the source information is saved in metadata.json.

**2. Segmentation and Tokenization**
The scraped text is then cleaned, divided into sentences and tokenized.
akcorp_package.segment_and_tokenize_verses("scraped_verses.json", "tokens_segmented.txt")
This produces tokens_segmented.txt. The original number of tokens is also saved in original_token_count.txt.

**3. Stopword Removal**
The stopword list is stored in akan_stopwords.json. The stopwords are removed from the tokenized corpus to produce final_verses.txt.

**4. POS Tagging and Corpus Search**
The project includes a lightweight Akan POS tagger trained on labelled data from the MasakhaPOS corpus. The trained model is stored in akcorp_package/models/twi_pos_model.pkl.
The model is used by the corpus search function. This makes it possible to search for words normally, with a regular expression, or by POS tag, for example [noun] or [verb]. 
akcorp_package.corpus_search("final_verses.txt", "search_results.txt", user_query)

**5. Corpus Analysis**
The comprehensive analysis function calculates word, bigram and trigram frequencies as well as character frequencies and collocation measures (PMI, t-score and Dice). It can also be used to focus on one particular word.
The corpus analysis function calculates the Type-Token Ratio (TTR) and creates a KWIC-style concordance for a chosen word.

**Output Files**
The main output files produced by the program are:
scraped_verses.json – scraped text
metadata.json – source metadata
tokens_segmented.txt – segmented and tokenized text
final_verses.txt – cleaned corpus after stopword removal
search_results.txt – corpus search results
comprehensive_analysis.txt – frequency and collocation results
search_analysis_results.txt – TTR and concordance results

**License**
MIT License
