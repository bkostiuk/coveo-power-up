import requests
import urllib3
import time
import json
from requests_html import HTMLSession
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# Get a list of urls for all movies at domain/start_url
def get_all_movie_page_urls(domain: str, start_url: str):
    page_html = requests.get(domain + start_url)
    soup = BeautifulSoup(page_html.content, "html.parser")
    link_count = 0
    links = []

    # Links to movies stored in .pagecontent > .lister > td.titleColumn > a [href]
    for td in soup.find_all('td', attrs={'class': 'titleColumn'}):
        tag = td.find('a')
        link = domain + tag['href']
        movie_details("Found url for {0} at {1}".format(tag.text, link))
        links.append(link)
        link_count += 1

    movie_details("Found {0} links on page {1}".format(link_count, domain + start_url))

# Get the movie details as a dictionary
def get_movie_details(movie_page_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        'Content-Type': 'text/html; charset=utf-8',
    }
    # driver = webdriver.Chrome(executable_path=r"../chromedriver.exe")
    # driver.get(movie_page_url)

    # wait = WebDriverWait(driver, 100)

    # # # # # wait for the content to be present
    # wait.until(EC.presence_of_element_located((By.ID, "titleStoryLine")))

    # driver.close()
    # soup = BeautifulSoup(driver.page_source, "html.parser")    
    
    page_html = requests.get(movie_page_url, headers=headers)
    soup = BeautifulSoup(page_html.text, "html.parser")
    
    retry_count = 0

    while(soup.find('div', attrs={'class': 'title_wrapper'}) == None):
        page_html = requests.get(movie_page_url, headers=headers)
        soup = BeautifulSoup(page_html.text, "html.parser")
        retry_count += 1

    print(retry_count)
    movie_details = dict()

    # Year: #titleYear > a[text]
    movie_details['year'] = get_num(soup.find('span', attrs={'id': 'titleYear'}).find('a').text)

    # Title: .title_wrapper > h1[text]
    movie_details['movieTitle'] = soup.find('div', attrs={'class': 'title_wrapper'}).find('h1').text.replace("({0})".format(movie_details['year']), '').strip()

    # Rated: .title_wrapper > .subtext[text] (trimmed)
    # Runtime: Runtime_str converted to minutes
    # Genre: .title_wrapper > a[text]
    details = soup.find('div', attrs={'class': 'title_wrapper'}).find('div', attrs={'class': 'subtext'}).text
    details_list = list(map(lambda x: x.strip(), details.split('|')))
    
    movie_details['rated'] = details_list[0]
    movie_details['runtimeStr'] = details_list[1]
    movie_details['genre'] = details_list[2]
    
    # Rating: .ratings_wrapper > .ratingValue > strong > span[text]
    movie_details['rating'] = float(soup.find('div', attrs={'class': 'ratings_wrapper'}).find('div', attrs={'class': 'ratingValue'}).find('strong').find('span').text.strip())

    # posterUri: .slate_wrapper > .poster > img[src]
    movie_details['posterUri'] = soup.find('div', attrs={'class': 'slate_wrapper'}).find('div', attrs={'class': 'poster'}).find('img')['src']
    
    # summary: div.plot_summary > div.summary_text[text]
    movie_details['summary'] = soup.find('div', attrs={'class': 'plot_summary'}).find('div', attrs={'class': 'summary_text'}).text.strip()

    # synopsis: div#titleStoryLine > p > span[text] (trimmed)
    movie_details['synopsis'] = soup.find('div', attrs={'id': 'titleStoryLine'}).find('p').find('span').text.strip()

    # Director: div.plot_summary > div.credit_summary_item[0] > a[text]
    # Writers: div.plot_summary > div.credit_summary_item[0] > a[text] (multiple),
    # Stars: div.plot_summary > div.credit_summary_item[0] > a[text] (except last)
    elems = soup.find('div', attrs={'class': 'plot_summary'}).find_all('div', attrs={'class': 'credit_summary_item'})

    directors = []
    for director in elems[0].find_all('a'):
        directors.append(director.text)
    movie_details['director'] = ', '.join(directors)

    writers = []
    for writer in elems[1].find_all('a'):
        writers.append(writer.text)
    movie_details['writer'] = ', '.join(writers)

    stars = []
    for star in elems[2].find_all('a'):
        stars.append(star.text)
    movie_details['stars'] = ', '.join(stars[:-1])

    # Trivia: ...
    movie_details['trivia'] = soup.find('div', attrs={'id': 'trivia'}).text.strip().replace('Trivia', '').replace('See more  »', '').strip()

    # Box office budget: div#titleDetails > ...
    # Runtime_str: .title_wrapper > time[text]
    for x in soup.find('div', attrs={'id': 'titleDetails'}).find_all('div', attrs={'class': 'txt-block'}):
        if(x.find('h4') and x.find('h4').text == 'Budget:'):
            movie_details['budget'] = get_num(x.text.strip())

        if(x.find('h4') and x.find('h4').text == 'Runtime:'):
            movie_details['runtime'] = get_num(x.text.strip())

    print(movie_details)

    # Dump to json
    with open("../results/{0}.json".format(movie_details['movieTitle']), 'w') as fp:
        json.dump(movie_details, fp)


def get_num(s : str):
    return int(''.join(filter(str.isdigit, s)))

# DOMAIN = "https://www.imdb.com"
# START_URL = "/chart/top?ref_=helpms_ih_gi_siteindex"

# get_all_movie_page_urls(DOMAIN, START_URL)

TEST_URL = "https://www.imdb.com/title/tt0111161/"
get_movie_details(TEST_URL)