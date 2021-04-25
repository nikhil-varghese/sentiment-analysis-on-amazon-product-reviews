import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pyLDAvis.sklearn
from collections import Counter
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from wordcloud import WordCloud, ImageColorGenerator

plt.style.use("seaborn-muted")
st.set_option('deprecation.showPyplotGlobalUse', False)

path = "./Cleaned Reviews/"

def visualize(filename):
	filepath = str(path) + str(filename)
	df = pd.read_pickle(filepath)

	st.markdown("# {} sentiment analysis".format(filename.split('_')[0]))

	avg_polarity = round(df['polarity'].mean(), 2)
	st.header(f"Average sentiment: {avg_polarity}")

	x_rating = df['rating'].value_counts().sort_index(ascending=False)
	polarity_avg = df.groupby('rating')['polarity'].mean()
	word_count_avg = df.groupby('rating')['word_count'].mean()
	subjectivity_avg = df.groupby('rating')['subjectivity'].mean()

	std_polarity = np.std(df['polarity'])

	# fig, ax = plt.subplots(3, 2)
	# num_bins = 20

	# ax[0][0].set_title('Sentiment Distribution')
	# n, bins, patches = ax[0][0].hist(df['polarity'], num_bins, density=True)
	# # add a 'best fit' line
	# y = ((1 / (np.sqrt(2 * np.pi) * std_polarity)) *
	#      np.exp(-0.5 * (1 / std_polarity * (bins - avg_polarity))**2))
	# ax[0][0].plot(bins, y, '-')

	# ax[1][0].set_title("Rating Distribution")
	# ax[1][0].bar(x_rating.index, x_rating)

	# ax[1][1].set_title("Average words by rating")
	# ax[1][1].bar(word_count_avg.index, word_count_avg)

	# ax[2][0].set_title("Average sentiment by rating")
	# ax[2][0].bar(polarity_avg.index, polarity_avg)

	# ax[2][1].set_title("Average subjectivity by rating")
	# ax[2][1].bar(subjectivity_avg.index, subjectivity_avg)

	# fig.tight_layout()
	# st.pyplot()


	fig1 = make_subplots(
	    rows=3, cols=2,
	    print_grid=True,
	    subplot_titles=("Polarity Distribution", "Subjectivity Distribution", "Ratings count", 
	    	"Average Word Count by rating", "Average Sentiment by rating", "Subjectivity by rating"))

	fig1.add_trace(
	    go.Histogram(x=df['polarity'], nbinsx=20),
	    row=1, col=1)

	fig1.add_trace(
	    go.Histogram(x=df['subjectivity'], nbinsx=20),
	    row=1, col=2)

	fig1.add_trace(
	    go.Bar(x=x_rating.index, y=x_rating),
	    row=2, col=1)

	fig1.add_trace(go.Bar(x=word_count_avg.index, y=word_count_avg),
			row=2, col=2)

	fig1.add_trace(
			go.Bar(x=subjectivity_avg.index, y=polarity_avg),
			row=3, col=1)

	fig1.add_trace(
			go.Bar(x=subjectivity_avg.index, y=subjectivity_avg),
			row=3, col=2)

	fig1.update_layout(height=1000, width=1000, template='ggplot2',
			title_text="Basic Summary", showlegend=False)
	st.plotly_chart(fig1)

	fig2 = px.scatter(df, x="polarity", y="subjectivity", color="rating",
    		title="Polarity vs Subjectivity Scatter plot",
    		)
	fig2.update_layout(height=700, width=1000,
    		template='seaborn')
	st.plotly_chart(fig2)

	df1 = df.loc[(df['rating'] >= 3) ]
	df2= df.loc[(df['rating'] < 3)]

	positive_reviews = df1['lemma_str'].tolist()
	if positive_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='summer').generate(str(positive_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Positive Reviews")
		st.pyplot()

	negative_reviews = df2['lemma_str'].tolist()
	if negative_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='autumn').generate(str(negative_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Negative Reviews")
		st.pyplot()

	best_review = df.sort_values(by=['helpful'], ascending=False)

	st.markdown("## Most Helpful Review")

	st.markdown("Rating : {}".format(best_review['rating'][0]))
	st.markdown("Upvotes : {}".format(best_review['helpful'][0]))
	st.markdown("Sentiment : {}".format(best_review['polarity'][0]))
	st.markdown("Subjectivity : {}".format(best_review['subjectivity'][0]))

	st.markdown(best_review['description'][0])

	extreme_positive_reviews = df.loc[(df['polarity'] == 1) & (df['subjectivity'] == 1)]['description'].head().tolist()
	extreme_negative_reviews = df.loc[(df['polarity'] == -1) & (df['subjectivity'] == 1)]['description'].head().tolist()

	st.markdown("## Extreme Positive Reviews")
	for i in extreme_positive_reviews:
		st.markdown(i)

	st.markdown("## Extreme Negative Reviews")
	for j in extreme_negative_reviews:
		st.markdown(j)
