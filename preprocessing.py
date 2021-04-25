import pandas as pd
import os
import re
import nltk
import streamlit as st
import pickle
import string
import contractions
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob

from scraper import product_name
from dashboard import visualize

def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wordnet.ADJ
    elif tag.startswith('V'):
        return wordnet.VERB
    elif tag.startswith('N'):
        return wordnet.NOUN
    elif tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def clean_data(df, title):
	df.drop(['title'], axis=1, inplace=True)
	df.dropna(axis=0, inplace=True)
	# df['rating'] = df['rating'].astype(int)
	# df['helpful'] = df['helpful'].astype(int)
	# Remove contractions
	df['no_contract_desc'] = df['description'].apply(lambda x: [contractions.fix(word) for word in x.split()])
	df['description_str'] = [' '.join(map(str, l)) for l in df['no_contract_desc']]


	df['tokenized'] = df['description_str'].apply(word_tokenize)
	df['lower'] = df['tokenized'].apply(lambda x: [word.lower() for word in x])
	print(f"Title: {title}")

	punc = string.punctuation
	df['no_punc'] = df['lower'].apply(lambda x: [word for word in x if word not in punc])

	stop_words = set(stopwords.words('english'))
	stop_words.add('book')
	product_name = re.findall(r'\w+', title.lower())
	print(product_name)
	more_stop_words = set(product_name)
	stop_words.update(more_stop_words)
	print(f"Stop words: {stop_words}")

	df['stopwords_removed'] = df['no_punc'].apply(lambda x: [word for word in x if word not in stop_words])

	df['pos_tags'] = df['stopwords_removed'].apply(nltk.tag.pos_tag)

	df['wordnet_pos'] = df['pos_tags'].apply(lambda x: [(word, get_wordnet_pos(pos_tag)) for (word, pos_tag) in x])

	wnl = WordNetLemmatizer()
	df['lemmatized'] = df['wordnet_pos'].apply(lambda x: [wnl.lemmatize(word, tag) for (word, tag) in x])

	df['lemma_str'] = [' '.join(map(str, l)) for l in df['lemmatized']]
	df['polarity'] = df['lemma_str'].apply(lambda x: round(TextBlob(x).sentiment.polarity, 3))
	df['subjectivity'] = df['lemma_str'].apply(lambda x: round(TextBlob(x).sentiment.subjectivity, 3))


	df['word_count'] = df['description'].apply(lambda x: len(str(x).split()))

	df = df[['rating', 'helpful', 'word_count', 'polarity', 'subjectivity', 'description', 'lemmatized', 'lemma_str']]

	path = "./Cleaned Reviews/"
	filename = title + "_cleaned.pkl"
	print(filename)
	df.to_pickle(os.path.join(path, filename))
	st.success("Data scraped, cleaned and saved.")

	visualize(filename)