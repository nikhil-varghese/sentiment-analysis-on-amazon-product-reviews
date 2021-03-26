import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

import seaborn as sns
from textblob import TextBlob
import pyLDAvis.sklearn
from collections import Counter
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from wordcloud import WordCloud, ImageColorGenerator

plt.style.use("seaborn-pastel")
st.set_option('deprecation.showPyplotGlobalUse', False)

path = "./Cleaned Reviews/"

def visualize(filename):
	filepath = str(path) + str(filename)
	df = pd.read_pickle(filepath)

	st.markdown("# {} sentiment analysis".format(filename.split('_')[0]))

	df['lemma_str'] = [' '.join(map(str, l)) for l in df['lemmatized']]
	df['sentiment'] = df['lemma_str'].apply(lambda x: TextBlob(x).sentiment.polarity)

	df['word_count'] = df['lemmatized'].apply(lambda x: len(str(x).split()))
	df['review_len'] = df['lemma_str'].apply(len)

	average_sentiment = round(df['sentiment'].mean(), 2)
	st.header(f"Mean of all the sentiment values: {average_sentiment}")

	plt.title('Sentiment Distribution')
	plt.hist(df['sentiment'], bins=50)
	plt.xlabel('Sentiment')
	plt.ylabel('Frequency')
	plt.grid()
	st.pyplot()

	x_rating = df['rating'].value_counts().sort_index(ascending=False)
	plt.title("Rating Distribution")
	plt.bar(x_rating.index, x_rating, alpha=0.8)
	plt.xlabel("Rating")
	plt.ylabel("Frequency")
	plt.grid()
	st.pyplot()

	plt.title('Percentage of ratings')
	plt.pie(x_rating, labels=x_rating.index,
	        autopct='%1.0f%%', pctdistance=0.7, labeldistance=1.1, wedgeprops=dict(width=0.5))
	plt.tight_layout()
	st.pyplot()

	polarity_avg = df.groupby('rating')['sentiment'].mean()
	plt.title("Average sentiment by rating")
	plt.bar(polarity_avg.index, polarity_avg)
	plt.xlabel('Rating')
	plt.ylabel('Average Sentiment')
	plt.grid()
	st.pyplot()

	words = df['lemmatized']
	allwords = []
	for wordlist in words:
	    allwords += wordlist

	mostcommon = FreqDist(allwords).most_common(50)

	wordcloud = WordCloud(background_color='white').generate(str(mostcommon))
	fig = plt.figure(figsize=(60, 60), facecolor='white')
	plt.imshow(wordcloud, interpolation='bilinear')
	plt.axis('off')
	plt.title("Most common 100 words")
	st.pyplot()

	mostcommon_small = FreqDist(allwords).most_common(25)
	x, y = zip(*mostcommon_small)
	plt.figure(figsize=(50,30))
	plt.margins(0.02)
	plt.bar(x, y)
	plt.xlabel('Words', fontsize=50)
	plt.ylabel('Frequency of Words', fontsize=50)
	plt.yticks(fontsize=40)
	plt.xticks(rotation=60, fontsize=40)
	plt.title('Frequency of 25 Most Common Words', fontsize=60)
	st.pyplot()
