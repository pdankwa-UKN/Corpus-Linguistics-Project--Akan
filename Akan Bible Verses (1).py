#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import unicodedata
from urllib.request import urlopen
from bs4 import BeautifulSoup

def scrape_verses(url, output_filename="scraped verses.json"):
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    verses = soup.find_all("span", class_="verse")
    raw_lines = [soup.title.text]

    for div in verses:
        text = div.get_text(" ", strip=True)
        raw_lines.append(text)

    json_data = {"raw_content": raw_lines}

    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    return json_data


url = "https://www.jw.org/tw/nhomakorabea/bible/nwt/nhoma/nnwom/119/"
scrape_verses(url)


# In[ ]:


import json
import requests
from bs4 import BeautifulSoup
import trafilatura

import json
import requests
import trafilatura
from bs4 import BeautifulSoup

def extract_metadata(url, output_filename="metadata.json"):
    # 1. Get Title, Date, and Publisher using trafilatura
    downloaded = trafilatura.fetch_url(url)
    metadata_extracted = trafilatura.extract_metadata(downloaded)

    # 2. Use BeautifulSoup to hunt for hidden Author and Copyright text patterns
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for specific copyright symbols or text containers at the bottom of the page
    copyright_text = "Not specified"
    copyright_elements = soup.find_all(string=lambda t: "©" in t or "Copyright" in t or "Watch Tower" in t)
    if copyright_elements:
        copyright_text = max([str(el).strip() for el in copyright_elements], key=len)

    # 3. Store results in a clean Python dictionary layout
    metadata_dict = {
        "title": metadata_extracted.title if metadata_extracted else "Not found",
        "source_publisher": metadata_extracted.sitename if (metadata_extracted and metadata_extracted.sitename) else "JW.ORG",
        "year_date": metadata_extracted.date if (metadata_extracted and metadata_extracted.date) else "2026",
        "author_speaker": "Watch Tower Bible and Tract Society",
        "license_copyright": copyright_text
    }

    # 4. Save dictionary automatically to a JSON file
    with open(output_filename, "w", encoding="utf-8") as json_file:
        json.dump(metadata_dict, json_file, ensure_ascii=False, indent=4)

    return metadata_dict


url = "https://jw.org"
extract_metadata(url)


# In[ ]:


import json
import re

def segment_and_tokenize_verses(input_json_path, output_txt_path):
    with open(input_json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    raw_lines = data.get("raw_content", [])
    all_final_sentences = []

    for line in raw_lines:
        # Step 1: Clean the initial messy symbols (\, *, +) but KEEP the periods
        cleaned_line = line.replace("\\", "").replace("*", "").replace("+", "").replace('"', '').strip()

        # Step 2: SENTENCE SEGMENTATION (Do this while periods are still intact!)
        # Splits text at periods while keeping the period attached to the sentence
        sentences = re.split(r'(?<=\.) ', cleaned_line)

        for s in sentences:
            clean_s = s.strip()

            # Skip empty sentences or lines that don't end with a period
            if clean_s and clean_s.endswith('.'):

                # Step 3: Remove leading verse numbers from the start of the sentence
                clean_s = re.sub(r'^\d+\s*', '', clean_s)

                # Step 4: WORD TOKENIZATION (Clean everything except the words inside this sentence)
                pattern = r"\w+(?:-\w+)*(?:'\w+)?|[\w\s]"
                tokens = re.findall(pattern, clean_s, flags=re.UNICODE)

                if tokens:
                    # Rejoin the clean tokens with spaces to rebuild a perfect, isolated sentence
                    rebuilt_sentence = " ".join(tokens)
                    all_final_sentences.append(rebuilt_sentence)

#write lines to file
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for sentence in all_final_sentences:
            out_file.write(sentence + "\n")

#Read file and print contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())

# Call function
segment_and_tokenize_verses("scraped verses.json", "tokens_segmented.txt")


# In[ ]:


import json
import re

akan_stopwords_list = ["o", "na", "ne", "enye", "dee", "mmom", "nti", "se", "a", "biara", "ho", "ha","mu", "so", "me", "wo", "ono", "ye", "mo", "won", "bi", "no", "yi",
"wei", "yei", "saa", "koraa", "enna", "anso", "nanso", "senea", "efiri","enam", "beye", "nyinaa", "kakra", "pii", "dodo", "ara", "nko", "nkutoo","paa", "ampaa", "mpo"]

# Save to the JSON file
with open("akan_stopwords.json", "w", encoding="utf-8") as f:
    json.dump(akan_stopwords_list, f, ensure_ascii=False, indent=4)
print("'akan_stopwords.json' saved .")

# Define the Cleaning Function

def create_clean_verses(input_txt_path, output_txt_path):
    # Load the stop words back from the JSON file
    with open("akan_stopwords.json", "r", encoding="utf-8") as f:
        akan_stopwords = json.load(f)

    # Build and compile the regex pattern using the loaded JSON data
    pattern = r'\b(' + '|'.join(re.escape(word) for word in akan_stopwords) + r')\b'
    stopword_regex = re.compile(pattern, flags=re.IGNORECASE)

    # Open the segmented tokens file using the function's input parameter
    with open(input_txt_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    verses = []

    # Loop through each line to remove stop words
    for line in lines:
        cleaned_verse = stopword_regex.sub('', line)
        cleaned_verse = re.sub(r'\s+', ' ', cleaned_verse).strip()

        if cleaned_verse:
            verses.append(cleaned_verse)
            print(cleaned_verse) 

    # Save the final output 
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for verse in verses:
            out_file.write(verse + "\n")

#Call Function
create_clean_verses("tokens_segmented.txt", "final_verses.txt")


# In[ ]:


#CORPUS SEARCH
import regex

def corpus_search(input_txt_path, output_txt_path, search_query):
    # 1. Load the tokens file
    with open(input_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Extract original tokens to check for capital letters (Proper Nouns)
    tokens_original = regex.findall(r'\b\p{L}+\b|[^\w\s]|\d+', text)
    total_tokens = len(tokens_original)

    tokens_lower = [t.lower() for t in tokens_original]

    # lower input and remove spaces
    query = search_query.strip().lower()

    search_lines = []
    context_window = 4  # Words to display on either side
    match_count = 0

    # Loop through and match against the 3 required types in lower
    for i in range(total_tokens):
        is_match = False
        token_low = tokens_lower[i]
        token_orig = tokens_original[i]

        # Annotation-based Search
        if query in ["[punc]", "[num]", "[prop]"]:
            if query == "[punc]" and regex.match(r'[^\w\s]', token_low):
                is_match = True
            elif query == "[num]" and regex.match(r'\d+', token_low):
                is_match = True
            elif query == "[prop]" and token_orig.isupper() and regex.match(r'\p{L}+', token_orig):
                is_match = True

        # Pattern-based / Regular Expression Search
        elif any(char in query for char in [".", "*", "+", "?", "^", "$", "[", "]"]):
            if regex.search(f"^{query}$", token_low):
                is_match = True

        # Keyword Search
        else:
            if token_low == query:
                is_match = True

        # If  match is found, take wmatche and word from left and right
        if is_match:
            match_count += 1
            left_context = tokens_original[max(0, i - context_window):i]
            right_context = tokens_original[i + 1:min(total_tokens, i + context_window + 1)]

            left_str = " ".join(left_context)
            right_str = " ".join(right_context)

# Save the clean match formatting using original casing for readability
            search_lines.append(f"Left: [{left_str}] --> MATCH: '{token_orig}' --> Right: [{right_str}]")

# create text report lines
    report_lines = [
        "=== CORPUS SEARCH RESULTS ===",
        f"User Query: '{search_query}'",
        f"Total Matches Found: {match_count}\n",
        "--- Match List ---"
    ] + search_lines + ["-" * 76]

#Write lines to file
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for line in report_lines:
            out_file.write(line + "\n")

#Read the file back and print contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())


#Interactive Mode
user_query = input("Enter word, regex (e.g., .*ɛ$), or annotation ([PUNC], [NUM], [PROP]): ")
corpus_search("final_verses.txt", "search_results.txt", user_query)


# In[ ]:


#'DATA ANALYSIS & N-GRAMS
import math
from collections import Counter
import regex

def comprehensive_analysis(input_txt_path, output_txt_path, choice_word=None):
    # Load the tokens file
    with open(input_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    text = text.lower()

    # Extract clean words using Unicode support
    words = regex.findall(r'\b\p{L}+\b', text)

    # 1. Base Counts & Frequencies
    N = len(words)  # Total word count tokens
    unigram_counts = Counter(words)

    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    bigram_counts = Counter(bigrams)

    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words) - 2)]
    trigram_counts = Counter(trigrams)

    characters = regex.findall(r'\p{L}', text)
    char_counts = Counter(characters)

    # 2. Advanced Collocation Metrics (PMI, t-score, Dice)
    collocation_results = []
    bigram_tuples = [(words[i], words[i+1]) for i in range(len(words) - 1)]
    tuple_counts = Counter(bigram_tuples)

    for bigram_tup, f_w1_w2 in tuple_counts.items():
        if f_w1_w2 < 2:  # Filter out rare single-occurrence pairs
            continue
        w1, w2 = bigram_tup
        f_w1 = unigram_counts[w1]
        f_w2 = unigram_counts[w2]

        expected = (f_w1 * f_w2) / N
        pmi = math.log2((f_w1_w2 * N) / (f_w1 * f_w2))
        t_score = (f_w1_w2 - expected) / math.sqrt(f_w1_w2)
        dice = (2 * f_w1_w2) / (f_w1 + f_w2)

        collocation_results.append({
            "bigram": f"{w1} {w2}",
            "freq": f_w1_w2,
            "pmi": round(pmi, 4),
            "t_score": round(t_score, 4),
            "dice": round(dice, 4)
        })

    # 3. Apply Interactive Filtering if a specific word was chosen
    if choice_word:
        target = choice_word.strip().lower()

        # Keep only counts/metrics containing the chosen word
        unigram_display = {w: f for w, f in unigram_counts.items() if w == target}
        bigram_display = {bg: f for bg, f in bigram_counts.items() if f" {target} " in f" {bg} "}
        trigram_display = {tg: f for tg, f in trigram_counts.items() if f" {target} " in f" {tg} "}
        collocation_display = [item for item in collocation_results if f" {target} " in f" {item['bigram']} "]
    else:
        # Default: Use the regular full top 10 lists
        unigram_display = dict(unigram_counts.most_common(10))
        bigram_display = dict(bigram_counts.most_common(10))
        trigram_display = dict(trigram_counts.most_common(10))
        collocation_display = collocation_results

    # Sort collocations by PMI score
    collocation_display.sort(key=lambda x: x["pmi"], reverse=True)

    # 4. Compile metrics sequentially into output lines
    analysis_lines = []

    if choice_word:
        analysis_lines.append(f"=== FILTERED CORPUS ANALYSIS FOR WORD: '{target}' ===\n")
    else:
        analysis_lines.append("=== STANDARD FREQUENCIES ===")

    analysis_lines.append("\n--- 1. Word Frequency / Unigrams ---")
    if unigram_display:
        for word, freq in unigram_display.items():
            analysis_lines.append(f"{word}: {freq}")
    else:
        analysis_lines.append("Word not found in corpus.")

    analysis_lines.append("\n--- 2. Bigrams ---")
    if bigram_display:
        for bg, freq in list(bigram_display.items())[:10]:
            analysis_lines.append(f"{bg}: {freq}")
    else:
        analysis_lines.append("No matching bigram patterns.")

    analysis_lines.append("\n--- 3. Trigrams ---")
    if trigram_display:
        for tg, freq in list(trigram_display.items())[:10]:
            analysis_lines.append(f"{tg}: {freq}")
    else:
        analysis_lines.append("No matching trigram patterns.")

    # Only include character data in the main comprehensive view
    if not choice_word:
        analysis_lines.append("\n--- 4. Character Frequency (Top 10 Letters) ---")
        for char, freq in char_counts.most_common(10):
            analysis_lines.append(f"{char}: {freq}")

    analysis_lines.append("\n\n=== COLLOCATION METRICS ===")
    analysis_lines.append(f"\n{'Bigram':<25} | {'Freq':<5} | {'PMI':<8} | {'t-score':<8} | {'Dice':<8}")
    analysis_lines.append("-" * 65)

    if collocation_display:
        for item in collocation_display[:10]:
            line = f"{item['bigram']:<25} | {item['freq']:<5} | {item['pmi']:<8} | {item['t_score']:<8} | {item['dice']:<8}"
            analysis_lines.append(line)
    else:
        analysis_lines.append("No collocation pairs match your criteria.")

#Write lines to file 
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for line in analysis_lines:
            out_file.write(line + "\n")

#Read the file back and print its contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())

#Interactive Mode
while True:
    print("\n" + "="*40)
    print("Choose Analysis Type:")
    print("1: Full Corpus Analysis (All Top 10 metrics)")
    print("2: Focused Word Analysis (Filters frequencies & collocations for one word)")
    print("3: Exit Analysis Menu")
    print("="*40)

    mode = input("Enter 1, 2, or 3: ").strip()

    if mode == "1":
        print("\nRunning Full Analysis...")
        comprehensive_analysis("final_verses.txt", "comprehensive_analysis.txt")
    elif mode == "2":
        selected_word = input("Enter the word you want to analyze (e.g., yehowa): ")
        comprehensive_analysis("final_verses.txt", "comprehensive_analysis.txt", selected_word)
    elif mode == "3":
        print("\nExiting Analysis Menu.")
        break
    else:
        print("\nInvalid choice. Please enter 1, 2, or 3.")


# In[ ]:


#CORPUS ANALYSIS
from collections import Counter
import regex

def corpus_analysis(input_txt_path, output_txt_path, search_keyword):
# Load the input file
    with open(input_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    text = text.lower()
    words = regex.findall(r'\b\p{L}+\b', text)
    total_tokens = len(words)

#Token-Type Ratio (TTR) Calculation
    unique_types = len(set(words))
    ttr = unique_types / total_tokens if total_tokens > 0 else 0

#Clean up user input keywords
    search_keyword = search_keyword.strip().lower()

    kwic_entries = []
    context_window = 4  # Words on either side

    for i, word in enumerate(words):
        if word == search_keyword:
            left_context = words[max(0, i - context_window):i]
            right_context = words[i + 1:min(total_tokens, i + context_window + 1)]

            left_str = " ".join(left_context)
            right_str = " ".join(right_context)

            entry_line = f"{left_str:>30} | {word:^12} | {right_str:<30}"
            kwic_entries.append(entry_line)

#creating text report lines
    report_lines = []

    report_lines.append("=== LINGUISTIC DIVERSITY (TTR) ===")
    report_lines.append(f"Total Word Tokens: {total_tokens}")
    report_lines.append(f"Unique Word Types: {unique_types}")
    report_lines.append(f"Token-Type Ratio (TTR): {round(ttr, 4)} ({round(ttr * 100, 2)}%)\n")

    report_lines.append("=== CONCORDANCE & KWIC ANALYSIS ===")
    report_lines.append(f"Target Search Term: '{search_keyword}' (Found {len(kwic_entries)} times)\n")
    report_lines.append(f"{'Left Context':>30} | {'Key Word':^12} | {'Right Context':<30}")
    report_lines.append("-" * 76)

    for line in kwic_entries:
        report_lines.append(line)

#Write lines to the file
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for line in report_lines:
            out_file.write(line + "\n")

#Read the file back and print its contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())

# Interactive Mode
user_keyword = input("Input the word you want to search (e.g., yehowa): ")
corpus_analysis("final_verses.txt", "search_analysis_results.txt", user_keyword)


# In[ ]:


import os

# Create the folder layout matching your notes
os.makedirs("akcorp_package", exist_ok=True)
print("Directory structure 'akcorp_package/' created successfully!")


# In[10]:


get_ipython().run_cell_magic('writefile', 'akcorp_package/corpli.py', '\nfrom urllib.request import urlopen\nimport json\nimport unicodedata\nimport re\nimport requests\nimport urllib.request\nimport regex\nimport math\nfrom collections import Counter\nfrom bs4 import BeautifulSoup\nimport trafilatura\n\n\ndef scrape_verses(url, output_filename="scraped verses.json"):\n    html = urlopen(url).read()\n    soup = BeautifulSoup(html, "html.parser")\n\n    verses = soup.find_all("span", class_="verse")\n    raw_lines = [soup.title.text]\n\n    for div in verses:\n        text = div.get_text(" ", strip=True)\n        raw_lines.append(text)\n\n    json_data = {"raw_content": raw_lines}\n\n    with open(output_filename, "w", encoding="utf-8") as json_file:\n        json.dump(json_data, json_file, ensure_ascii=False, indent=4)\n\n    return json_data\n\n\nurl = "https://www.jw.org/tw/nhomakorabea/bible/nwt/nhoma/nnwom/119/"\nscrape_verses(url)\n\ndef extract_metadata(url, output_filename="metadata.json"):\n    # 1. Get Title, Date, and Publisher using trafilatura\n    downloaded = trafilatura.fetch_url(url)\n    metadata_extracted = trafilatura.extract_metadata(downloaded)\n\n    # 2. Use BeautifulSoup to hunt for hidden Author and Copyright text patterns\n    headers = {\'User-Agent\': \'Mozilla/5.0 (Windows NT 10.0; Win64; x64)\'}\n    response = requests.get(url, headers=headers, timeout=10)\n    soup = BeautifulSoup(response.text, \'html.parser\')\n\n    # Look for specific copyright symbols or text containers at the bottom of the page\n    copyright_text = "Not specified"\n    copyright_elements = soup.find_all(string=lambda t: "©" in t or "Copyright" in t or "Watch Tower" in t)\n    if copyright_elements:\n        copyright_text = max([str(el).strip() for el in copyright_elements], key=len)\n\n    # 3. Store results in a clean Python dictionary layout\n    metadata_dict = {\n        "title": metadata_extracted.title if metadata_extracted else "Not found",\n        "source_publisher": metadata_extracted.sitename if (metadata_extracted and metadata_extracted.sitename) else "JW.ORG",\n        "year_date": metadata_extracted.date if (metadata_extracted and metadata_extracted.date) else "2026",\n        "author_speaker": "Watch Tower Bible and Tract Society",\n        "license_copyright": copyright_text\n    }\n\n    # 4. Save dictionary automatically to a JSON file\n    with open(output_filename, "w", encoding="utf-8") as json_file:\n        json.dump(metadata_dict, json_file, ensure_ascii=False, indent=4)\n\n    return metadata_dict\n\n\nurl = "https://jw.org"\nextract_metadata(url)\n\ndef segment_and_tokenize_verses(input_json_path, output_txt_path):\n    with open(input_json_path, "r", encoding="utf-8") as file:\n        data = json.load(file)\n\n    raw_lines = data.get("raw_content", [])\n    all_final_sentences = []\n\n    for line in raw_lines:\n        # Step 1: Clean the initial messy symbols (\\, *, +) but KEEP the periods\n        cleaned_line = line.replace("\\\\", "").replace("*", "").replace("+", "").replace(\'"\', \'\').strip()\n\n        # Step 2: SENTENCE SEGMENTATION (Do this while periods are still intact!)\n        # Splits text at periods while keeping the period attached to the sentence\n        sentences = re.split(r\'(?<=\\.) \', cleaned_line)\n\n        for s in sentences:\n            clean_s = s.strip()\n\n            # Skip empty sentences or lines that don\'t end with a period\n            if clean_s and clean_s.endswith(\'.\'):\n\n                # Step 3: Remove leading verse numbers from the start of the sentence\n                clean_s = re.sub(r\'^\\d+\\s*\', \'\', clean_s)\n\n                # Step 4: WORD TOKENIZATION (Clean everything except the words inside this sentence)\n                pattern = r"\\w+(?:-\\w+)*(?:\'\\w+)?|[\\w\\s]"\n                tokens = re.findall(pattern, clean_s, flags=re.UNICODE)\n\n                if tokens:\n                    # Rejoin the clean tokens with spaces to rebuild a perfect, isolated sentence\n                    rebuilt_sentence = " ".join(tokens)\n                    all_final_sentences.append(rebuilt_sentence)\n\n#write lines to file\n    with open(output_txt_path, "w", encoding="utf-8") as out_file:\n        for sentence in all_final_sentences:\n            out_file.write(sentence + "\\n")\n\n#Read file and print contents\n    with open(output_txt_path, "r", encoding="utf-8") as read_file:\n        print(read_file.read())\n\n# Call function\nsegment_and_tokenize_verses("scraped verses.json", "tokens_segmented.txt")\n\nakan_stopwords_list = ["o", "na", "ne", "enye", "dee", "mmom", "nti", "se", "a", "biara", "ho", "ha","mu", "so", "me", "wo", "ono", "ye", "mo", "won", "bi", "no", "yi",\n"wei", "yei", "saa", "koraa", "enna", "anso", "nanso", "senea", "efiri","enam", "beye", "nyinaa", "kakra", "pii", "dodo", "ara", "nko", "nkutoo","paa", "ampaa", "mpo"]\n\n# Save to the JSON file\nwith open("akan_stopwords.json", "w", encoding="utf-8") as f:\n    json.dump(akan_stopwords_list, f, ensure_ascii=False, indent=4)\nprint("\'akan_stopwords.json\' saved .")\n\n# Define the Cleaning Function\n\ndef create_clean_verses(input_txt_path, output_txt_path):\n    # Load the stop words back from the JSON file\n    with open("akan_stopwords.json", "r", encoding="utf-8") as f:\n        akan_stopwords = json.load(f)\n\n    # Build and compile the regex pattern using the loaded JSON data\n    pattern = r\'\\b(\' + \'|\'.join(re.escape(word) for word in akan_stopwords) + r\')\\b\'\n    stopword_regex = re.compile(pattern, flags=re.IGNORECASE)\n\n    # Open the segmented tokens file using the function\'s input parameter\n    with open(input_txt_path, "r", encoding="utf-8") as file:\n        lines = file.readlines()\n\n    verses = []\n\n    # Loop through each line to remove stop words\n    for line in lines:\n        cleaned_verse = stopword_regex.sub(\'\', line)\n        cleaned_verse = re.sub(r\'\\s+\', \' \', cleaned_verse).strip()\n\n        if cleaned_verse:\n            verses.append(cleaned_verse)\n            print(cleaned_verse) \n\n    # Save the final output \n    with open(output_txt_path, "w", encoding="utf-8") as out_file:\n        for verse in verses:\n            out_file.write(verse + "\\n")\n\n#Call Function\ncreate_clean_verses("tokens_segmented.txt", "final_verses.txt")\n\ndef corpus_search(input_txt_path, output_txt_path, search_query):\n    # 1. Load the tokens file\n    with open(input_txt_path, "r", encoding="utf-8") as file:\n        text = file.read()\n\n    # Extract original tokens to check for capital letters (Proper Nouns)\n    tokens_original = regex.findall(r\'\\b\\p{L}+\\b|[^\\w\\s]|\\d+\', text)\n    total_tokens = len(tokens_original)\n\n    tokens_lower = [t.lower() for t in tokens_original]\n\n    # lower input and remove spaces\n    query = search_query.strip().lower()\n\n    search_lines = []\n    context_window = 4  # Words to display on either side\n    match_count = 0\n\n    # Loop through and match against the 3 required types in lower\n    for i in range(total_tokens):\n        is_match = False\n        token_low = tokens_lower[i]\n        token_orig = tokens_original[i]\n\n        # Annotation-based Search\n        if query in ["[punc]", "[num]", "[prop]"]:\n            if query == "[punc]" and regex.match(r\'[^\\w\\s]\', token_low):\n                is_match = True\n            elif query == "[num]" and regex.match(r\'\\d+\', token_low):\n                is_match = True\n            elif query == "[prop]" and token_orig.isupper() and regex.match(r\'\\p{L}+\', token_orig):\n                is_match = True\n\n        # Pattern-based / Regular Expression Search\n        elif any(char in query for char in [".", "*", "+", "?", "^", "$", "[", "]"]):\n            if regex.search(f"^{query}$", token_low):\n                is_match = True\n\n        # Keyword Search\n        else:\n            if token_low == query:\n                is_match = True\n\n        # If  match is found, take wmatche and word from left and right\n        if is_match:\n            match_count += 1\n            left_context = tokens_original[max(0, i - context_window):i]\n            right_context = tokens_original[i + 1:min(total_tokens, i + context_window + 1)]\n\n            left_str = " ".join(left_context)\n            right_str = " ".join(right_context)\n\n# Save the clean match formatting using original casing for readability\n            search_lines.append(f"Left: [{left_str}] --> MATCH: \'{token_orig}\' --> Right: [{right_str}]")\n\n# create text report lines\n    report_lines = [\n        "=== CORPUS SEARCH RESULTS ===",\n        f"User Query: \'{search_query}\'",\n        f"Total Matches Found: {match_count}\\n",\n        "--- Match List ---"\n    ] + search_lines + ["-" * 76]\n\n#Write lines to file\n    with open(output_txt_path, "w", encoding="utf-8") as out_file:\n        for line in report_lines:\n            out_file.write(line + "\\n")\n\n#Read the file back and print contents\n    with open(output_txt_path, "r", encoding="utf-8") as read_file:\n        print(read_file.read())\n\n\n#Interactive Mode\nuser_query = input("Enter word, regex (e.g., .*ɛ$), or annotation ([PUNC], [NUM], [PROP]): ")\ncorpus_search("final_verses.txt", "search_results.txt", user_query)\n\ndef comprehensive_analysis(input_txt_path, output_txt_path, choice_word=None):\n    # Load the tokens file\n    with open(input_txt_path, "r", encoding="utf-8") as file:\n        text = file.read()\n\n    text = text.lower()\n\n    # Extract clean words using Unicode support\n    words = regex.findall(r\'\\b\\p{L}+\\b\', text)\n\n    # 1. Base Counts & Frequencies\n    N = len(words)  # Total word count tokens\n    unigram_counts = Counter(words)\n\n    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]\n    bigram_counts = Counter(bigrams)\n\n    trigrams = [f"{words[i]} {words[i+1]} {words[i+2]}" for i in range(len(words) - 2)]\n    trigram_counts = Counter(trigrams)\n\n    characters = regex.findall(r\'\\p{L}\', text)\n    char_counts = Counter(characters)\n\n    # 2. Advanced Collocation Metrics (PMI, t-score, Dice)\n    collocation_results = []\n    bigram_tuples = [(words[i], words[i+1]) for i in range(len(words) - 1)]\n    tuple_counts = Counter(bigram_tuples)\n\n    for bigram_tup, f_w1_w2 in tuple_counts.items():\n        if f_w1_w2 < 2:  # Filter out rare single-occurrence pairs\n            continue\n        w1, w2 = bigram_tup\n        f_w1 = unigram_counts[w1]\n        f_w2 = unigram_counts[w2]\n\n        expected = (f_w1 * f_w2) / N\n        pmi = math.log2((f_w1_w2 * N) / (f_w1 * f_w2))\n        t_score = (f_w1_w2 - expected) / math.sqrt(f_w1_w2)\n        dice = (2 * f_w1_w2) / (f_w1 + f_w2)\n\n        collocation_results.append({\n            "bigram": f"{w1} {w2}",\n            "freq": f_w1_w2,\n            "pmi": round(pmi, 4),\n            "t_score": round(t_score, 4),\n            "dice": round(dice, 4)\n        })\n\n    # 3. Apply Interactive Filtering if a specific word was chosen\n    if choice_word:\n        target = choice_word.strip().lower()\n\n        # Keep only counts/metrics containing the chosen word\n        unigram_display = {w: f for w, f in unigram_counts.items() if w == target}\n        bigram_display = {bg: f for bg, f in bigram_counts.items() if f" {target} " in f" {bg} "}\n        trigram_display = {tg: f for tg, f in trigram_counts.items() if f" {target} " in f" {tg} "}\n        collocation_display = [item for item in collocation_results if f" {target} " in f" {item[\'bigram\']} "]\n    else:\n        # Default: Use the regular full top 10 lists\n        unigram_display = dict(unigram_counts.most_common(10))\n        bigram_display = dict(bigram_counts.most_common(10))\n        trigram_display = dict(trigram_counts.most_common(10))\n        collocation_display = collocation_results\n\n    # Sort collocations by PMI score\n    collocation_display.sort(key=lambda x: x["pmi"], reverse=True)\n\n    # 4. Compile metrics sequentially into output lines\n    analysis_lines = []\n\n    if choice_word:\n        analysis_lines.append(f"=== FILTERED CORPUS ANALYSIS FOR WORD: \'{target}\' ===\\n")\n    else:\n        analysis_lines.append("=== STANDARD FREQUENCIES ===")\n\n    analysis_lines.append("\\n--- 1. Word Frequency / Unigrams ---")\n    if unigram_display:\n        for word, freq in unigram_display.items():\n            analysis_lines.append(f"{word}: {freq}")\n    else:\n        analysis_lines.append("Word not found in corpus.")\n\n    analysis_lines.append("\\n--- 2. Bigrams ---")\n    if bigram_display:\n        for bg, freq in list(bigram_display.items())[:10]:\n            analysis_lines.append(f"{bg}: {freq}")\n    else:\n        analysis_lines.append("No matching bigram patterns.")\n\n    analysis_lines.append("\\n--- 3. Trigrams ---")\n    if trigram_display:\n        for tg, freq in list(trigram_display.items())[:10]:\n            analysis_lines.append(f"{tg}: {freq}")\n    else:\n        analysis_lines.append("No matching trigram patterns.")\n\n    # Only include character data in the main comprehensive view\n    if not choice_word:\n        analysis_lines.append("\\n--- 4. Character Frequency (Top 10 Letters) ---")\n        for char, freq in char_counts.most_common(10):\n            analysis_lines.append(f"{char}: {freq}")\n\n    analysis_lines.append("\\n\\n=== COLLOCATION METRICS ===")\n    analysis_lines.append(f"\\n{\'Bigram\':<25} | {\'Freq\':<5} | {\'PMI\':<8} | {\'t-score\':<8} | {\'Dice\':<8}")\n    analysis_lines.append("-" * 65)\n\n    if collocation_display:\n        for item in collocation_display[:10]:\n            line = f"{item[\'bigram\']:<25} | {item[\'freq\']:<5} | {item[\'pmi\']:<8} | {item[\'t_score\']:<8} | {item[\'dice\']:<8}"\n            analysis_lines.append(line)\n    else:\n        analysis_lines.append("No collocation pairs match your criteria.")\n\n#Write lines to file \n    with open(output_txt_path, "w", encoding="utf-8") as out_file:\n        for line in analysis_lines:\n            out_file.write(line + "\\n")\n\n#Read the file back and print its contents\n    with open(output_txt_path, "r", encoding="utf-8") as read_file:\n        print(read_file.read())\n\n#Interactive Mode\nwhile True:\n    print("\\n" + "="*40)\n    print("Choose Analysis Type:")\n    print("1: Full Corpus Analysis (All Top 10 metrics)")\n    print("2: Focused Word Analysis (Filters frequencies & collocations for one word)")\n    print("3: Exit Analysis Menu")\n    print("="*40)\n\n    mode = input("Enter 1, 2, or 3: ").strip()\n\n    if mode == "1":\n        print("\\nRunning Full Analysis...")\n        comprehensive_analysis("final_verses.txt", "comprehensive_analysis.txt")\n    elif mode == "2":\n        selected_word = input("Enter the word you want to analyze (e.g., yehowa): ")\n        comprehensive_analysis("final_verses.txt", "comprehensive_analysis.txt", selected_word)\n    elif mode == "3":\n        print("\\nExiting Analysis Menu.")\n        break\n    else:\n        print("\\nInvalid choice. Please enter 1, 2, or 3.")\n\n\ndef corpus_analysis(input_txt_path, output_txt_path, search_keyword):\n# Load the input file\n    with open(input_txt_path, "r", encoding="utf-8") as file:\n        text = file.read()\n\n    text = text.lower()\n    words = regex.findall(r\'\\b\\p{L}+\\b\', text)\n    total_tokens = len(words)\n\n#Token-Type Ratio (TTR) Calculation\n    unique_types = len(set(words))\n    ttr = unique_types / total_tokens if total_tokens > 0 else 0\n\n#Clean up user input keywords\n    search_keyword = search_keyword.strip().lower()\n\n    kwic_entries = []\n    context_window = 4  # Words on either side\n\n    for i, word in enumerate(words):\n        if word == search_keyword:\n            left_context = words[max(0, i - context_window):i]\n            right_context = words[i + 1:min(total_tokens, i + context_window + 1)]\n\n            left_str = " ".join(left_context)\n            right_str = " ".join(right_context)\n\n            entry_line = f"{left_str:>30} | {word:^12} | {right_str:<30}"\n            kwic_entries.append(entry_line)\n\n#creating text report lines\n    report_lines = []\n\n    report_lines.append("=== LINGUISTIC DIVERSITY (TTR) ===")\n    report_lines.append(f"Total Word Tokens: {total_tokens}")\n    report_lines.append(f"Unique Word Types: {unique_types}")\n    report_lines.append(f"Token-Type Ratio (TTR): {round(ttr, 4)} ({round(ttr * 100, 2)}%)\\n")\n\n    report_lines.append("=== CONCORDANCE & KWIC ANALYSIS ===")\n    report_lines.append(f"Target Search Term: \'{search_keyword}\' (Found {len(kwic_entries)} times)\\n")\n    report_lines.append(f"{\'Left Context\':>30} | {\'Key Word\':^12} | {\'Right Context\':<30}")\n    report_lines.append("-" * 76)\n\n    for line in kwic_entries:\n        report_lines.append(line)\n\n#Write lines to the file\n    with open(output_txt_path, "w", encoding="utf-8") as out_file:\n        for line in report_lines:\n            out_file.write(line + "\\n")\n\n#Read the file back and print its contents\n    with open(output_txt_path, "r", encoding="utf-8") as read_file:\n        print(read_file.read())\n\n# Interactive Mode\nuser_keyword = input("Input the word you want to search (e.g., yehowa): ")\ncorpus_analysis("final_verses.txt", "search_analysis_results.txt", user_keyword)\n\n\n\n')


# In[11]:


get_ipython().run_cell_magic('writefile', 'akcorp_package/_init_.py', '# Marks this directory as a Python package module layout\nfrom .corpli import scrape_verses, extract_metadata, segment_and_tokenize_verses, create_clean_verses, corpus_search, comprehensive_analysis, corpus_analysis\n')


# In[12]:


import os

folder = "akcorp_package"
if os.path.exists(folder):
    print(f"📁 Files inside '{folder}':", os.listdir(folder))
else:
    print(f"❌ The folder '{folder}' does not exist in this directory!")


# In[13]:


import akcorp_package

# 1. Setup the inputs
url = "https://jw.org"
json_file = "final_verses.json"
text_file = "final_verses.txt"

print("--- STEP 1: SCRAPING ---")
akcorp_package.scrape_verses(url, json_file)

print("\n--- STEP 2: SEGMENTATION & TOKENIZATION ---")
akcorp_package.segment_and_tokenize_verses(json_file, text_file)

print("\n--- STEP 3: INTERACTIVE MODE ---")
# This will trigger your keyword search and analysis tools
akcorp_package.corpus_analysis(text_file, "search_analysis_results.txt")


# In[14]:


get_ipython().run_cell_magic('writefile', 'setup.py', 'from setuptools import setup, find_packages\n\nsetup(\n    name="akcorp_package",\n    version="0.1.0",\n    packages=find_packages(),\n    install_requires=["requests", "beautifulsoup4", "trafilatura", "lxml_html_clean","regex"],)\n')


# In[15]:


get_ipython().run_cell_magic('writefile', 'requirements.txt', 'requests\nbeautifulsoup4\ntrafilatura\nlxml_html_clean\nregex\n')

