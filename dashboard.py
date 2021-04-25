import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

import seaborn as sns
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

	df['helpful'] = df['helpful'].astype(int)
	best_review = df.sort_values(by=['helpful'], ascending=False)['description'][0]

	average_sentiment = round(df['polarity'].mean(), 2)
	st.header(f"Average sentiment: {average_sentiment}")

	st.markdown("## Most Helpful Review")
	st.markdown("### {}".format(best_review))

	fig, ax = plt.subplots(2, 2)

	ax[0][0].set_title('Sentiment Distribution')
	ax[0][0].hist(df['polarity'], bins=50)
	ax[0][0].grid()

	x_rating = df['rating'].value_counts().sort_index(ascending=False)
	ax[0][1].set_title("Rating Distribution")
	ax[0][1].bar(x_rating.index, x_rating, alpha=0.8)


	polarity_avg = df.groupby('rating')['polarity'].mean()
	ax[1][0].set_title("Average sentiment by rating")
	ax[1][0].bar(polarity_avg.index, polarity_avg)

	ax[1][0].grid()

	word_count_avg = df.groupby('rating')['word_count'].mean()
	ax[1][1].set_title("Average words by rating")
	ax[1][1].bar(word_count_avg.index, word_count_avg)
	fig.tight_layout()
	st.pyplot()

	df1 = df.loc[(df['rating'] >= 3) ]
	df2= df.loc[(df['rating'] < 3)]

	positive_reviews = df1['lemma_str'].tolist()
	print(f"Positive reviews: {positive_reviews}")
	if positive_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='summer').generate(str(positive_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Positive Reviews")
		st.pyplot()

	negative_reviews = df2['lemma_str'].tolist()
	print(f"Negative Reviews: {negative_reviews}")
	if negative_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='autumn').generate(str(negative_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Negative Reviews")
		st.pyplot()

	# mostcommon_small = FreqDist(allwords).most_common(25)
	# x, y = zip(*mostcommon_small)
	# plt.figure(figsize=(50,30))
	# plt.margins(0.02)
	# plt.bar(x, y)
	# plt.xlabel('Words', fontsize=50)
	# plt.ylabel('Frequency of Words', fontsize=50)
	# plt.yticks(fontsize=40)
	# plt.xticks(rotation=60, fontsize=40)
	# plt.title('Frequency of 25 Most Common Words', fontsize=60)
	# st.pyplot()
