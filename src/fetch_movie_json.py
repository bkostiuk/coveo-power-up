import requests
from bs4 import BeautifulSoup

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
        print("Found url for {0} at {1}".format(tag.text, link))
        links.append(link)
        link_count += 1

    print("Found {0} links on page {1}".format(link_count, domain + start_url))

DOMAIN = "https://www.imdb.com"
START_URL = "/chart/top?ref_=helpms_ih_gi_siteindex"

get_all_movie_page_urls(DOMAIN, START_URL)