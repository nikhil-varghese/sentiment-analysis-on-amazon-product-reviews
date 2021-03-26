import pandas as pd
import nltk
import pickle
import string
import fasttext
import contractions
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer
from scraper import product_name
import streamlit as st

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
	# Remove contractions
	df['no_contract_desc'] = df['description'].apply(lambda x: [contractions.fix(word) for word in x.split()])
	df['description_str'] = [' '.join(map(str, l)) for l in df['no_contract_desc']]

	#pretrained_model = "/home/nik/Downloads/lid.176.bin"
	#model = fasttext.load_model(pretrained_model)

	#langs = []
	#for sent in df['description_str']:
	#    lang = model.predict(sent)[0]
	#    langs.append(str(lang)[11:13])

	#df['langs'] = langs
	#df = df.loc[df['langs'] == 'en']

	df['tokenized'] = df['description_str'].apply(word_tokenize)
	df['lower'] = df['tokenized'].apply(lambda x: [word.lower() for word in x])

	punc = string.punctuation
	df['no_punc'] = df['lower'].apply(lambda x: [word for word in x if word not in punc])

	stop_words = set(stopwords.words('english'))
	df['stopwords_removed'] = df['no_punc'].apply(lambda x: [word for word in x if word not in stop_words])

	df['pos_tags'] = df['stopwords_removed'].apply(nltk.tag.pos_tag)

	df['wordnet_pos'] = df['pos_tags'].apply(lambda x: [(word, get_wordnet_pos(pos_tag)) for (word, pos_tag) in x])

	wnl = WordNetLemmatizer()
	df['lemmatized'] = df['wordnet_pos'].apply(lambda x: [wnl.lemmatize(word, tag) for (word, tag) in x])
	df = df[['rating', 'lemmatized']]

	df.to_pickle(f"./Cleaned Reviews/{title}_cleaned.pkl")
	st.success("Data scraped, cleaned and saved.")
