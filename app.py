import streamlit as st
import pandas as pd
import scraper
import dashboard
import preprocessing
import os

path = "./Cleaned Reviews/"

def main():
	page = st.sidebar.selectbox(
		'Select Page', ['Home', "Sentiment Analysis"])

	if page == 'Home':
		homepage()
	else:
		analysis_page()

def homepage():
	st.title("Enter Amazon product url to fetch data")
	url = st.text_input("")
	if st.button('Fetch Data'):
		all_reviews_df, product_title = scraper.scraper(url)
		if all_reviews_df is not None:
			st.dataframe(all_reviews_df.head())
			title = preprocessing.product_name(product_title)
			# all_reviews_df.to_csv(f"./Amazon Reviews/{title}.csv")
			preprocessing.clean_data(all_reviews_df, title)

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
		dashboard.visualize(str(option))


main()
