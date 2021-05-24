import os
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from collections import Counter
from wordcloud import WordCloud, ImageColorGenerator

plt.style.use("seaborn-muted")
st.set_option('deprecation.showPyplotGlobalUse', False)

path = "./Cleaned Reviews/"

def visualize(filename):
	"""
		Function to visualize Amazon reviews

		Input: Filename of cleaned dataset
	"""
	filepath = str(path) + str(filename)
	df = pd.read_pickle(filepath)

	st.markdown("# {} sentiment analysis".format(filename.split('_')[0]))

	avg_polarity = round(df['polarity'].mean(), 2)
	median_polarity = round(df['polarity'].median(), 2)
	st.header(f"Mean sentiment: {avg_polarity}")
	st.header(f"Median sentiment: {median_polarity}")

	x_rating = df['rating'].value_counts().sort_index(ascending=False)
	polarity_avg = df.groupby('rating')['polarity'].mean()
	word_count_avg = df.groupby('rating')['word_count'].mean()
	subjectivity_avg = df.groupby('rating')['subjectivity'].mean()

	# Sentiment Distribution
	st.markdown("### Polarity")
	st.markdown("Polarity represents the emotion in a review. Its value ranges from -1 to 1.\
			If polarity is 1, the sentiment in the review is highly positive.\
			Else, if it is -1, the sentiment is highly negative. If polarity is 0, sentiment is neutral.")
	st.markdown("### Subjectivity")
	st.markdown("Subjectivity represents how opinionated a review is. Its value ranges from 0 to 1. If the value is 0, the review is based on facts.\
			Else if the value is 1, the review is highly opinionated.")

	fig1 = make_subplots(
	    rows=1, cols=2,
	    subplot_titles=("Polarity Distribution", "Subjectivity Distribution"))

	fig1.add_trace(
	    go.Histogram(x=df['polarity'], nbinsx=20),
	    row=1, col=1)

	fig1.add_trace(
	    go.Histogram(x=df['subjectivity'], nbinsx=20),
	    row=1, col=2)

	fig1.update_traces(marker_color='rgb(8,23,154)', opacity=0.4)

	fig1.update_layout(height=400, width=1000, template='ggplot2',
			title_text="Sentiment", showlegend=False)

	st.plotly_chart(fig1)

	# Basic Statistics
	fig2 = make_subplots(
		rows=2, cols=2,
		subplot_titles=("Ratings count", "Average Word Count by rating",
			"Average Sentiment by rating", "Subjectivity by rating"))

	fig2.add_trace(
	    go.Bar(x=x_rating.index, y=x_rating),
	    row=1, col=1)

	fig2.add_trace(go.Bar(x=word_count_avg.index, y=word_count_avg),
			row=1, col=2)

	fig2.add_trace(
			go.Bar(x=subjectivity_avg.index, y=polarity_avg),
			row=2, col=1)

	fig2.add_trace(
			go.Bar(x=subjectivity_avg.index, y=subjectivity_avg),
			row=2, col=2)

	fig2.update_traces(marker_color='rgb(58,102,225)', marker_line_color='rgb(8,38,57)',
                  marker_line_width=2.5, opacity=0.6)

	fig2.update_layout(height=800, width=1000, template='ggplot2',
			title_text="Basic Summary", showlegend=False, bargap=0.3)
	st.plotly_chart(fig2)

	# Polarity vs Subjectivity scatter plot
	fig3 = px.scatter(df, x="polarity", y="subjectivity", color="rating",
    		title="Polarity vs Subjectivity Scatter plot",
    		)
	fig3.update_layout(height=700, width=1000,
    		template='seaborn')
	st.plotly_chart(fig3)

	df1 = df.loc[(df['rating'] >= 3) ]
	df2= df.loc[(df['rating'] < 3)]

	# Positive review WordCloud
	positive_reviews = df1['lemma_str'].tolist()
	if positive_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='summer').generate(str(positive_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Positive Reviews")
		st.pyplot()

	# Negative review WordCloud
	negative_reviews = df2['lemma_str'].tolist()
	if negative_reviews != []:
		wordcloud = WordCloud(width=1000, height=600, background_color='white', colormap='autumn').generate(str(negative_reviews))
		fig = plt.figure(figsize=(10, 10), facecolor='white')
		plt.imshow(wordcloud, interpolation='bilinear')
		plt.axis('off')
		plt.title("Negative Reviews")
		st.pyplot()
	# Most helpful review
	best_review = df.sort_values(by=['helpful'], ascending=False)

	st.markdown("## Most Helpful Review")

	st.markdown("Rating : {}".format(best_review['rating'][0]))
	st.markdown("Upvotes : {}".format(best_review['helpful'][0]))
	st.markdown("Sentiment : {}".format(best_review['polarity'][0]))
	st.markdown("Subjectivity : {}".format(best_review['subjectivity'][0]))

	st.markdown(best_review['description'][0])
	# Extreme Reviews
	extreme_positive_reviews = df.loc[(df['polarity'] == 1) & (df['subjectivity'] == 1)]['description'].head().tolist()
	extreme_negative_reviews = df.loc[(df['polarity'] == -1) & (df['subjectivity'] == 1)]['description'].head().tolist()

	st.markdown("## Extreme Positive Reviews")
	for i in extreme_positive_reviews:
		st.markdown(i)

	st.markdown("## Extreme Negative Reviews")
	for j in extreme_negative_reviews:
		st.markdown(j)
