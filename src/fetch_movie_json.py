import requests
import json
from bs4 import BeautifulSoup

## Runs a script to scrape the top 250 IMDB movies along with
## related information and write to json files in ../dataset

DOMAIN = "https://www.imdb.com"
START_URL = "/chart/top?ref_=helpms_ih_gi_siteindex"

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
    return links

# Get the movie details as a dictionary
def get_movie_details(movie_page_url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
        'Content-Type': 'text/html; charset=utf-8',
    }
    page_html = requests.get(movie_page_url, headers=headers)
    soup = BeautifulSoup(page_html.text, "html.parser")
    
    retry_count = 0

    while(soup.find('div', attrs={'class': 'title_wrapper'}) == None):
        page_html = requests.get(movie_page_url, headers=headers)
        soup = BeautifulSoup(page_html.text, "html.parser")
        retry_count += 1

    print("Page requests: " + str(retry_count))
    movie_details = dict()

    # Set movie url
    movie_details['uri'] = movie_page_url

    # Year: span#titleYear > a[text]
    movie_details['year'] = get_num(soup.find('span', attrs={'id': 'titleYear'}).find('a').text)

    # Title: div.title_wrapper > h1[text]
    movie_details['movieTitle'] = soup.find('div', attrs={'class': 'title_wrapper'}).find('h1').text.replace("({0})".format(movie_details['year']), '').strip()

    # Genre: div#titleStoryLine > h4 > a
    for div in soup.find('div', attrs={'id': 'titleStoryLine'}).find_all('div'):
        if div.find('h4') and div.find('h4').text == 'Genres:':
            movie_details['genre'] = ','.join(map(lambda x: x.text.strip(), div.find_all('a')))
        if div.find('h4') and div.find('h4').text == 'Certificate:':
            # TODO Figure this out for certificate
            pass
    
    # Rating: div.ratings_wrapper > div.ratingValue > strong > span[text]
    movie_details['rating'] = float(soup.find('div', attrs={'class': 'ratings_wrapper'}).find('div', attrs={'class': 'ratingValue'}).find('strong').find('span').text.strip())

    # posterUri: div.slate_wrapper > .poster > img[src]
    movie_details['posterUri'] = soup.find('div', attrs={'class': 'poster'}).find('img')['src']
    
    # summary: div.plot_summary > div.summary_text[text]
    movie_details['summary'] = soup.find('div', attrs={'class': 'plot_summary'}).find('div', attrs={'class': 'summary_text'}).text.strip()

    # synopsis: div#titleStoryLine > p > span[text] (trimmed)
    movie_details['synopsis'] = soup.find('div', attrs={'id': 'titleStoryLine'}).find('p').find('span').text.strip()
    
    elems = soup.find('div', attrs={'class': 'plot_summary'}).find_all('div', attrs={'class': 'credit_summary_item'})
    # Director: div.plot_summary > div.credit_summary_item[0] > a[text]
    directors = []
    for director in elems[0].find_all('a'):
        directors.append(director.text)
    movie_details['director'] = ','.join(directors)

    # Writers: div.plot_summary > div.credit_summary_item[0] > a[text] (multiple)
    writers = []
    for writer in elems[1].find_all('a'):
        writers.append(writer.text)

    if len(writers) > 2:
        # Remove 'See more'
        movie_details['writer'] = ','.join(writers[:-1])
    else:
        movie_details['writer'] = ','.join(writers)
    
    # Stars: div.plot_summary > div.credit_summary_item[0] > a[text] (except last)
    stars = []
    for star in elems[2].find_all('a'):
        stars.append(star.text)
    movie_details['stars'] = ','.join(stars[:-1])

    # Trivia: div#trivia[text] (Remove 'See more' and 'Trivia')
    movie_details['trivia'] = soup.find('div', attrs={'id': 'trivia'}).text.strip().replace('Trivia', '').replace('See more  »', '').strip()

    # Box office budget: div#titleDetails > div > h4[text == 'Budget:']
    # Languages: div#titleDetails > div > h4[text == 'Language:'] (Contatenate multiple)
    # Runtime: div#titleDetails > div > h4[text == 'Runtime:']
    for x in soup.find('div', attrs={'id': 'titleDetails'}).find_all('div', attrs={'class': 'txt-block'}):
        if(x.find('h4') and x.find('h4').text == 'Budget:'):
            # Just get the numbers
            movie_details['budget'] = get_num(x.text.strip())

        if(x.find('h4') and x.find('h4').text == 'Runtime:'):
            movie_details['runtime'] = get_num(x.text.strip().split('|')[0])

        if(x.find('h4') and x.find('h4').text == 'Language:'):
            movie_details['languages'] = ','.join(map(lambda lang: lang.text.strip(), x.find_all('a')))
    
    print(movie_details)
    return movie_details

# Write content to json file in dataset
def write_to_json_file(filename, content):
    filename = filename.replace(':', '').replace('-', '').replace('/', ' ')
    with open("../dataset/{0}.json".format(filename), 'w') as f:
        json.dump(content, f)

# Get only the numbers from a string
def get_num(s : str):
    return int(''.join(filter(str.isdigit, s)))

def main():
    for url in get_all_movie_page_urls(DOMAIN, START_URL):
        print("Running url: " + url)
        details = get_movie_details(url)
        write_to_json_file(details['movieTitle'], details)

if __name__ == '__main__':
    main()