# Import necessary libraries
import requests
import lxml
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import math
import time
import streamlit as st
import os

import nltk
import pickle
import string
import fasttext
import contractions
import matplotlib.pyplot as plt
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import WordNetLemmatizer

import seaborn as sns
from textblob import TextBlob
import pyLDAvis.sklearn
from collections import Counter
from nltk.probability import FreqDist
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from wordcloud import WordCloud, ImageColorGenerator


plt.style.use("seaborn-pastel")

url = "https://amazon.in"

path = "./Cleaned Reviews/"

# Function to scrape the reviews
def review_parse(url):
	page_content = bs(url.content, 'lxml')
	reviews_list = page_content.find(id='cm_cr-review_list')

	df = pd.DataFrame(columns = ['rating', 'title', 'description'])
	# time.sleep(5)

	for item in range(10):
		try:
			rating = (reviews_list.find_all(class_="review-rating"))[item].text[:3]
		except:
			rating = None
		try:
			title = (reviews_list.find_all(class_="review-title"))[item].text.replace('\n', '')
		except:
			title = None
		try:
			description = (reviews_list.find_all(class_="review-text"))[item].text.replace('\n', '')
		except:
			description = None

		df = df.append({'rating': rating, 'title': title,
						'description': description}, ignore_index=True)

		# print(df.iloc[item])


	return df


def scraper(product_url):
	# Scrape the product page for required data
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
	# product_url = "https://www.amazon.in/gp/product/0198700989/ref=ox_sc_saved_title_5?smid=AT95IG9ONZD7S&psc=1"
	try:
		product_page = requests.get(product_url, headers=headers)
		print(product_page.status_code)

		product_page_parsed = bs(product_page.content, 'lxml')

		# Product name
		product_title = product_page_parsed.find(id='productTitle').text.strip('\n')
		st.header(product_title)
	except:
		st.error("Please enter a valid amazon.in product url")
		return None, 1

	try:
		# Average rating for the product
		average_rating = product_page_parsed.find('i', class_='a-icon-star').text[:3]
		st.subheader(f"Average Rating:  {average_rating}")

		num_ratings = product_page_parsed.find(id='acrCustomerReviewText').text[:-7]
		# num_ratings = int(num_ratings[0].text[:-15])
		st.subheader(f"No. of ratings: {num_ratings}")

		url_match = product_page_parsed.find("a", class_="a-link-emphasis a-text-bold")["href"]

		reviews_url = "https://www.amazon.in" + url_match + "&pageNumber="
		# print(reviews_url)

		reviews_page = requests.get(reviews_url, headers=headers)
		# print(reviews_page.status_code)

		reviews_page_parsed = bs(reviews_page.content, 'html.parser')

		ratings_dist = []
		for i in reviews_page_parsed.find_all('div', class_='a-meter'):
		    ratings_dist.append(int(i['aria-label'].strip('%')))
		s_customer = ratings_dist[0] + ratings_dist[1]

		st.subheader(f"4 stars and above: {s_customer}%")

		reviews_list = reviews_page_parsed.find(id='cm_cr-review_list')

		# Find total number of reviews to calculate the number of pages to be scraped
		num_reviews = reviews_page_parsed.find(id='filter-info-section').div.text.replace('\n', '').strip()
		num_reviews = num_reviews.split('|')[1][1:-14]
		num_reviews = int(num_reviews.replace(',',''))
		st.subheader(f"No. of reviews: {num_reviews}")

		page_limit = math.ceil(num_reviews/10)
		# print(page_limit)

		all_reviews_df = pd.DataFrame(columns = ['rating', 'title', 'description'])
		# print(all_reviews_df.head())
		page = 1
		latest_iteration = st.empty()
		bar = st.progress(0)
		# Call parse function to scrape the reviews
		while page <= page_limit:
			full_url = reviews_url + str(page)
			print(f"Page = {page}/{page_limit}")
			get_url = requests.get(full_url)
			print(get_url.status_code)

			while get_url.status_code != 200:
				time.sleep(2)
				print("Retrying......")
				get_url = requests.get(full_url)
				print(get_url.status_code)

			partial_df = review_parse(get_url)
			progress = round((page/page_limit)*100)
			all_reviews_df = all_reviews_df.append(partial_df, ignore_index=True)
			bar.progress(progress)
			latest_iteration.text(f"Scraping {progress}% completed.")
			page += 1
			if page > page_limit:
				print("Completed.")
		return all_reviews_df, product_title

	except:
		st.warning("No reviews for the product")
		return None, 1

def product_name(product_title):
	title = product_title.split('/')
	title = ' '.join(title)
	return title


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

	pretrained_model = "/home/nik/Downloads/lid.176.bin"
	model = fasttext.load_model(pretrained_model)

	langs = []
	for sent in df['description_str']:
	    lang = model.predict(sent)[0]
	    langs.append(str(lang)[11:13])

	df['langs'] = langs
	df = df.loc[df['langs'] == 'en']

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


def data_viz(filename):
	filepath = str(path) + str(filename)
	df = pd.read_pickle(filepath)

	st.markdown("# {} sentiment analysis".format(filename.split('_')[0]))

	df['lemma_str'] = [' '.join(map(str, l)) for l in df['lemmatized']]
	df['sentiment'] = df['lemma_str'].apply(lambda x: TextBlob(x).sentiment.polarity)

	df['word_count'] = df['lemmatized'].apply(lambda x: len(str(x).split()))
	df['review_len'] = df['lemma_str'].apply(len)

	average_sentiment = round(df['sentiment'].mean(), 2)
	st.subheader(f"Average sentiment: {average_sentiment}")

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
	plt.title("Average sentiment per rating")
	plt.bar(polarity_avg.index, polarity_avg)
	plt.xlabel('Rating')
	plt.ylabel('Average Sentiment')
	plt.grid()
	st.pyplot()

	# words = df['lemmatized']
	# allwords = []
	# for wordlist in words:
	#     allwords += wordlist

	# mostcommon = FreqDist(allwords).most_common(10)

	# wordcloud = WordCloud(background_color='white').generate(str(mostcommon))
	# fig = plt.figure(figsize=(30, 20), facecolor='white')
	# plt.imshow(wordcloud, interpolation='bilinear')
	# plt.axis('off')
	# plt.title("Top most common 100 words")
	# st.pyplot()

def homepage():
	st.title("Enter Amazon product url to fetch data")
	url = st.text_input("Enter url for an amazon product")
	if st.button('Start scraping'):
		all_reviews_df, product_title = scraper(url)
		if product_title != 1:
			title = product_name(product_title)
			clean_data(all_reviews_df, title)

def analysis_page():
	directory = os.listdir(path)
	review_data = []
	for files in review_data:
		review_data.append(files)
	print(review_data)
	option = st.sidebar.selectbox(
		'Select Dataset to visualize',
		directory
		)

	with st.spinner("Loading Visualization"):
		data_viz(str(option))

def main():
	page = st.sidebar.selectbox(
		'Select Page', ['Home', "Sentiment Analysis"])

	if page == 'Home':
		homepage()
	else:
		analysis_page()

main()