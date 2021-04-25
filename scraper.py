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


url = "https://amazon.in"


# Function to scrape the reviews
def review_parse(url):
	page_content = bs(url.content, 'lxml')
	reviews_list = page_content.find(id='cm_cr-review_list')

	df = pd.DataFrame(columns = ['rating', 'title', 'description', 'helpful'])
	# time.sleep(5)

	for item in range(10):
		try:
			rating = int(reviews_list.find_all(class_="review-rating")[item].text[:1])
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
		try:
			helpful = int(reviews_list.find_all(class_="cr-vote-text")[item].text.split(" ")[0])
		except:
			helpful = 0

		df = df.append({'rating': rating, 'title': title,
			'description': description, 'helpful': helpful}, ignore_index=True)
	return df


def scraper(product_url):
	# Scrape the product page for required data
	headers = {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
	# product_url = "https://www.amazon.in/gp/product/0198700989/ref=ox_sc_saved_title_5?smid=AT95IG9ONZD7S&psc=1"
	try:
		product_page = requests.get(product_url, headers=headers)
		print(product_page.status_code)

		product_page_parsed = bs(product_page.content, 'lxml')

		# Product name
		product_title = product_page_parsed.find(id='productTitle').text.strip('\n')
		st.header(product_title)
	except:
		print(product_page_parsed.prettify())
		st.error("Please enter a valid amazon.in product url")
		return None
	try:
		# Average rating for the product
		average_rating = product_page_parsed.find('i',
								class_='a-icon-star').text[:3]
		st.subheader(f"Average Rating:  {average_rating}")

		num_ratings = product_page_parsed.find(id='acrCustomerReviewText').text[:-7]
		# num_ratings = int(num_ratings[0].text[:-15])
		st.subheader(f"No. of ratings: {num_ratings}")

		url_match = product_page_parsed.find("a",
			class_="a-link-emphasis a-text-bold")["href"]

		reviews_url = "https://www.amazon.in" + url_match + "&pageNumber="
		print(reviews_url)

		reviews_page = requests.get(reviews_url, headers=headers)
		print(reviews_page.status_code)

		reviews_page_parsed = bs(reviews_page.content, 'html.parser')
		# print(reviews_page_parsed)
		ratings_dist = []
		print(100*"*")
		ratings_list = reviews_page_parsed.find_all('div',
									class_='a-link-normal')
		print(ratings_list)
		if ratings_list != []:
			for i in ratings_list:
				print("Looping ratings")
				ratings_dist.append(int(i['aria-label'].strip('%')))
			s_customer = ratings_dist[0] + ratings_dist[1]
			print(ratings_dist)
			print(s_customer)
			st.subheader(f"4 stars and above: {s_customer}%")

		reviews_list = reviews_page_parsed.find(id='cm_cr-review_list')

		# Find total number of reviews, to calculate the number of pages to be scraped
		num_reviews = reviews_page_parsed.find(id='filter-info-section').div.text.replace('\n', '').strip()
		num_reviews = num_reviews.split('|')[1][1:-14]
		num_reviews = int(num_reviews.replace(',',''))
		st.subheader(f"No. of reviews: {num_reviews}")

		page_limit = math.ceil(num_reviews/10)
		print(page_limit)

		all_reviews_df = pd.DataFrame(columns = ['rating', 'title',
													'description'])
		print(all_reviews_df.head())
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
			all_reviews_df = all_reviews_df.append(partial_df,
				ignore_index=True)
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
