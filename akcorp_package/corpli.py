#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from bs4 import BeautifulSoup
import json
import requests
import unicodedata

#SCRAPING
# HTTP header to mimic browser 
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Books to scrape 
bible_books= ["genesis", "exodus", "leviticus", "numeri", "yosua"]

# raw results
scraped_verses = {}

print("Scraping...")

for book in bible_books:
    print(f"Scraping book contents for: {book}")

    #iterate chapter by chapter
    chapter = 1
    while True:
        url = f"https://www.jw.org/tw/nhomakorabea/bible/nwt/nhoma/{book}/{chapter}/"
        response = requests.get(url, headers=HEADERS)

        # If a chapter doesn't exist break the book loop 
        if response.status_code != 200:
            break

        # Parse HTML text content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        verses = soup.find_all("span", class_="verse")

        # Process title headers 
        pages = [
            soup.title.text if soup.title else f"{book.capitalize()} {chapter}"
        ]
        for div in verses:
            text = div.get_text(" ", strip=True)

            #Unicode normalization
            text = unicodedata.normalize("NFC", text)
            pages.append(text)

        # data collection
        scraped_verses[f"{book}_chapter_{chapter}"] = {
            "url": url,
            "raw_content": pages,
        }

        # Step cleanly to the next sequential chapter pointer
        chapter += 1

# Save into a single file
output_filename = "scraped_verses.json"
with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(scraped_verses, f, ensure_ascii=False, indent=4)

print(f"{output_filename} saved")


# In[ ]:



# METADATA EXTRACTION

try:
    downloaded = trafilatura.fetch_url("https://jw.org")
    metadata_extracted = trafilatura.extract_metadata(downloaded)
    title = metadata_extracted.title if metadata_extracted else "Nhomakorabea - JW.ORG"
except Exception:
    title = "Nhomakorabea - JW.ORG"

#Edit book names ("genesis" -> "Genesis")
scraped_books = [book.replace("-", " ").title() for book in books_actually_used]

metadata_dict = {
    "title": title,
    "source_publisher": "JW.ORG",
    "year_date": "2026",
    "author_speaker": "Watch Tower Bible and Tract Society",
    "books_scraped": scraped_books  
}

# Save metadata 
with open("metadata.json", "w", encoding="utf-8") as json_file:
    json.dump(metadata_dict, json_file, ensure_ascii=False, indent=4)

print("Saved: 'scraped_verses.json' and 'metadata.json'")


# In[ ]:


import json
import re

def segment_and_tokenize_verses(input_json_path, output_txt_path):
    with open(input_json_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    all_final_sentences = []

    for page_key in data:
        raw_lines = data[page_key].get("raw_content", [])


        for line in raw_lines:
        # Clean the initial messy symbols (\, *, +) but KEEP the periods
            cleaned_line = line.replace("\\", "").replace("*", "").replace("+", "").replace('"', '').strip()

        # SEGMENTATION - Splits text at periods while keeping the period attached to the sentence
            sentences = re.split(r'(?<=\.) ', cleaned_line)

            for s in sentences:
                clean_s = s.strip()

            # Skip empty sentences or lines that don't end with a period
                if clean_s and clean_s.endswith('.'):

                #Remove leading verse numbers from the start of the sentence
                    clean_s = re.sub(r'^\d+\s*', '', clean_s)

                #TOKENIZATION -Clean everything except the words inside sentence
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


    #Count the total tokens before stopwords are removed
    total_token_count = 0
    for sentence in all_final_sentences:
        total_token_count += len(sentence.split())

    print(f"Total tokens before stopwords removal): {total_token_count}")

    # Save to text file for corpus search
    with open("original_token_count.txt", "w", encoding="utf-8") as count_file:
        count_file.write(str(total_token_count))

# Read file and print contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())


# Call function
segment_and_tokenize_verses("scraped_verses.json", "tokens_segmented.txt")


# In[ ]:

#STOPWORD CREATION AND REMOVAL
import json
import re

akan_stopwords_list = ["o", "na", "ne", "enye", "dee", "mmom", "nti", "se", "a", "biara", "ho", "ha","mu", "so", "me", "wo", "ono", "ye", "mo", "won", "bi", "no", "yi",
"wei", "yei", "saa", "koraa", "enna", "anso", "nanso", "senea", "efiri","enam", "beye", "nyinaa", "kakra", "pii", "dodo", "ara", "nko", "nkutoo","paa", "ampaa", "mpo"]

# Save to the JSON file
with open("akan_stopwords.json", "w", encoding="utf-8") as f:
    json.dump(akan_stopwords_list, f, ensure_ascii=False, indent=4)
print("'akan_stopwords.json' saved .")


#CLEANING AND SEGMENTATION
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

#TAGGER TRAINING
import pickle                                    
from nltk.tag.perceptron import PerceptronTagger  #POS tagger model to train
 
def load_data(file_name):
    sentences = []           
    current_sentence = []    
 
    with open(file_name, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip() 
 
            if line == "":
                # A blank line marks the end of a sentence
                if len(current_sentence) > 0:
                    sentences.append(current_sentence)  
                    current_sentence = []                
            else:
                # A non-blank line is one "word tag" pair
                parts = line.split()
                word = parts[0]  # the word itself
                tag = parts[1]   # its correct part-of-speech tag
                current_sentence.append((word, tag))  # add this (word, tag) pair to the current sentence
 
    return sentences 
 
print("Loading data files...")
train_data = load_data("train.txt")  # training sentences
test_data = load_data("test.txt")    # test sentences 

 # start a fresh, untrained tagger and train it on our own labeled Akan sentences
print("Training the tagger...")
tagger = PerceptronTagger(load=False) 
tagger.train(train_data)                
 
# check how many tags it gets right
accuracy = tagger.accuracy(test_data)  
print("Tagger Accuracy:", accuracy)

# save the trained tagger  
print("Saving model to disk...")
with open("twi_pos_model.pkl", "wb") as output_file:
    pickle.dump(tagger, output_file)  so we can reload it later without retraining
 
print("Done!")


# In[ ]:


# CORPUS SEARCH - POS TAGGING & ANNOTATIONS
import os
import pickle
import regex

def corpus_search(input_txt_path, output_txt_path, search_query):
    
    # Loading trained tagger
    base_dir = os.path.dirname(__file__) if "__file__" in locals() else os.getcwd()
    model_path = os.path.join(base_dir, "akcorp_package", "models", "twi_pos_model.pkl")

    if os.path.exists(model_path):
        with open(model_path, "rb") as f:
            akan_tagger = pickle.load(f)
    else:
        akan_tagger = None
  
    # 1. Load the tokens file
    with open(input_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Extract original tokens
    tokens_original = regex.findall(r'\b\p{L}+\b|[^\w\s]|\d+', text)
    total_tokens = len(tokens_original)
    tokens_lower = [t.lower() for t in tokens_original]

    # Run tagger 
    if akan_tagger:
        tagged_pairs = akan_tagger.tag(tokens_original)
        # Convert to a dictionary 
        tag_dict = dict(tagged_pairs)
    else:
        tag_dict = {}

    # Lower input and remove spaces
    query = search_query.strip().lower()

    search_lines = []
    context_window = 4  # Words to display on either side
    match_count = 0

    # Loop through and match against the required types
    for i in range(total_tokens):
        is_match = False
        token_low = tokens_lower[i]
        token_orig = tokens_original[i]

        # Grab the tag we computed in the background for this exact word token
        token_tag = tag_dict.get(token_orig, "UNKNOWN")

        # 1. annotation Search (e.g., [noun], [verb], [punct])
        if query.startswith("[") and query.endswith("]"):
            target_tag = query.strip("[]").upper()
            if token_tag.upper() == target_tag:
                is_match = True

        # 2.Regular Expression Search
        elif any(char in query for char in [".", "*", "+", "?", "^", "$", "[", "]"]):
            if regex.search(f"^{query}$", token_low):
                is_match = True

        # 3. word Search 
        else:
            if token_low == query:
                is_match = True

        # IF ANY OF THE 3 SEARCH TYPES MATCHED, EXTRACT CONTEXT AND SHOW THE TAG
        if is_match:
            match_count += 1
            left_context = tokens_original[max(0, i - context_window):i]
            right_context = tokens_original[i + 1:min(total_tokens, i + context_window + 1)]

            left_str = " ".join(left_context)
            right_str = " ".join(right_context)

            search_lines.append(f"Left: [{left_str}] --> MATCH: '{token_orig}' ({token_tag}) --> Right: [{right_str}]")

    # pretty printing
    report_lines = [
        "CORPUS SEARCH RESULTS",
        f"User Query: '{search_query}'",
        f"Total Matches Found: {match_count}\n",
        "Matches"
    ] + search_lines + ["-" * 76]

    # Write lines to file
    with open(output_txt_path, "w", encoding="utf-8") as out_file:
        for line in report_lines:
            out_file.write(line + "\n")

    # Read the file back and print contents
    with open(output_txt_path, "r", encoding="utf-8") as read_file:
        print(read_file.read())

# Interactive Mode
user_query = input("Enter word, regex (e.g., .*ɛ$), or annotation tag (e.g., [noun]): ")
corpus_search("final_verses.txt", "search_results.txt", user_query)


# In[ ]:


#DATA ANALYSIS & N-GRAMS
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

    # 3. Interactive Filter
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
        analysis_lines.append(f"CORPUS ANALYSIS FOR WORD: '{target}'\n")
    else:
        analysis_lines.append("STANDARD FREQUENCIES")

    analysis_lines.append("\n 1. Word Frequency / Unigrams")
    if unigram_display:
        for word, freq in unigram_display.items():
            analysis_lines.append(f"{word}: {freq}")
    else:
        analysis_lines.append("Word not found in corpus.")

    analysis_lines.append("\n 2. Bigrams ")
    if bigram_display:
        for bg, freq in list(bigram_display.items())[:10]:
            analysis_lines.append(f"{bg}: {freq}")
    else:
        analysis_lines.append("No matching bigram patterns.")

    analysis_lines.append("\n 3. Trigrams ")
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
import os
from collections import Counter
import regex

def corpus_analysis(input_txt_path, output_txt_path, search_keyword):

    with open(input_txt_path, "r", encoding="utf-8") as file:
        text = file.read()

    text = text.lower()
    words = regex.findall(r'\b\p{L}+\b', text)
    total_tokens = len(words)

#Token-Type Ratio (TTR) Calculation
    unique_types = len(set(words))
    ttr = unique_types / total_tokens if total_tokens > 0 else 0

    #Loadtoken count before stopword removal
    original_tokens = "Unknown"
    if os.path.exists("original_token_count.txt"):
        with open("original_token_count.txt", "r", encoding="utf-8") as count_file:
            original_tokens = count_file.read().strip()

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

    report_lines.append(" TOKEN TYPE RATIO ")
    # NEW LINES: Display both counts side-by-side for comparison
    report_lines.append(f"Original Tokens (Before Stopwords): {original_tokens}")
    report_lines.append(f"Cleaned Word Tokens (After Stopwords): {total_tokens}")
    report_lines.append(f"Unique Word Types: {unique_types}")
    report_lines.append(f"Token-Type Ratio (TTR): {round(ttr, 4)} ({round(ttr * 100, 2)}%)\n")

    report_lines.append(" CONCORDANCE & KWIC ANALYSIS ")
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





