# Import necessary libraries
import requests
import lxml
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import math
import time
import streamlit as st


st.title("Amazon product review analysis")

url = "https://amazon.in"

url = st.text_input("Enter url for an amazon product")
# Function to scrape the reviews
def review_parse(url):
	page_content = bs(url.content, 'lxml')
	reviews_list = page_content.find(id='cm_cr-review_list')

	df = pd.DataFrame(columns = ['rating', 'rating_title', 'rating_description'])
	# time.sleep(5)

	for item in range(10):
		try:
			rating = (reviews_list.find_all(class_="review-rating"))[item].text[:3]
		except:
			rating = None
		try:
			rating_title = (reviews_list.find_all(class_="review-title"))[item].text.replace('\n', '')
		except:
			rating_title = None
		try:
			rating_description = (reviews_list.find_all(class_="review-text"))[item].text.replace('\n', '')
		except:
			rating_description = None

		df = df.append({'rating': rating, 'rating_title': rating_title,
						'rating_description': rating_description}, ignore_index=True)

		# print(df.iloc[item])


	return df


def scraper(product_url):
	# Scrape the product page for required data
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
	# product_url = "https://www.amazon.in/gp/product/0198700989/ref=ox_sc_saved_title_5?smid=AT95IG9ONZD7S&psc=1"
	product_page = requests.get(product_url, headers=headers)
	print(product_page.status_code)

	product_page_parsed = bs(product_page.content, 'lxml')

	# Product name
	product_title = product_page_parsed.find(id='productTitle').text.strip('\n')
	st.header(product_title)

	# Average rating for the product
	average_rating = product_page_parsed.find('i', class_='a-icon-star').text[:3]
	st.subheader(f"Average Rating:  {average_rating}")

	num_ratings = product_page_parsed.find(id='acrCustomerReviewText').text[:-8]
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
	num_reviews = num_reviews.split('|')[1][1:-15]
	num_reviews = int(num_reviews.replace(',',''))
	st.subheader(f"No. of reviews: {num_reviews}")

	page_limit = math.ceil(num_reviews/10)
	# print(page_limit)

	all_reviews_df = pd.DataFrame(columns = ['rating', 'rating_title', 'rating_description'])
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
		latest_iteration.text(f"Scraping {progress}% completed.")
		bar.progress(progress)
		page += 1
		if page == page_limit:
			print("Completed.")


	return all_reviews_df, product_title

def product_name(product_title):
	title = product_title.split(' ')
	title = ' '.join(title[:3])
	title = title.split('/')
	title = ' '.join(title)
	return title
# Save the dataframe of reviews to a csv file
if st.button('Start scraping'):
	all_reviews_df, product_title = scraper(url)
	st.write(all_reviews_df)
	title = product_name(product_title)
	all_reviews_df.to_csv(f"./{title} reviews.csv")
	st.write(f"Saved as '{title} reviews.csv'")

