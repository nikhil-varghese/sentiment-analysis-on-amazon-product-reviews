# Import necessary libraries
import requests
import lxml
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as bs
import math


headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
product_url = "https://www.amazon.in/gp/product/0198700989/ref=ox_sc_saved_title_5?smid=AT95IG9ONZD7S&psc=1"
product_page = requests.get(product_url, headers=headers)
print(product_page.status_code)

product_page_parsed = bs(product_page.content, 'lxml')


product_title = product_page_parsed.find('title').text

print(product_title)

average_rating = product_page_parsed.find('i', class_='a-icon-star').text[:3]
print(f"Average Rating:  {average_rating}")

num_ratings = product_page_parsed.find(id='acrCustomerReviewText').text[:-8]
# num_ratings = int(num_ratings[0].text[:-15])
print(f"No. of ratings: {num_ratings}")

url_match = product_page_parsed.find("a", class_="a-link-emphasis a-text-bold")["href"]

reviews_url = "https://www.amazon.in" + url_match + "&pageNumber="
print(reviews_url)

reviews_page = requests.get(reviews_url, headers=headers)
print(reviews_page.status_code)

reviews_page_parsed = bs(reviews_page.content, 'html.parser')

ratings_dist = []
for i in reviews_page_parsed.find_all('div', class_='a-meter'):
    ratings_dist.append(int(i['aria-label'].strip('%')))
s_customer = ratings_dist[0] + ratings_dist[1]

print(f"4 stars and above: {s_customer}%")

reviews_list = reviews_page_parsed.find(id='cm_cr-review_list')

all_reviews_df = pd.DataFrame(columns = ['rating', 'rating_title', 'rating_description'])

def review_parse(reviews_url):
	page_content = bs(reviews_url.content, 'lxml')
	reviews_list = reviews_page_parsed.find(id='cm_cr-review_list')
	df = pd.DataFrame(columns = ['rating', 'rating_title', 'rating_description'])

	for item in reviews_list:
		try:
			rating = item.find('i', class_="review-rating").text[:3]
			# print(rating)
		except:
			rating = None
		try:
			rating_title = item.find('a', class_="review-title").text
		except:
			rating_title = None
		try:
			rating_description = item.find('span', class_="review-text").text
		except:
			rating_description = None

		df = df.append({'rating': rating, 'rating_title': rating_title,
						'rating_description': rating_description}, ignore_index=True)

	return df

num_reviews = reviews_page_parsed.find(id='filter-info-section').div.text.replace('\n', '').strip()
num_reviews = num_reviews.split('|')[1][1:-15]
num_reviews = int(num_reviews.replace(',',''))
print(num_reviews)


page_limit = math.ceil(num_reviews/10)
print(page_limit)

page = 1
while page <= page_limit:
	full_url = reviews_url + str(page)
	print(full_url)
	get_url = requests.get(full_url)

	partial_df = review_parse(get_url)

	all_reviews_df = all_reviews_df.append(partial_df, ignore_index=True)
	page += 1

all_reviews_df.to_csv('reviews.csv')
print("Saved to csv")

