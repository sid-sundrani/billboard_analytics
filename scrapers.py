# Note: All lyrics scraped from AZLyrics are only being used for education purposes 

import requests 
from bs4 import BeautifulSoup
import html
import time
import random
from contextlib import closing
from bs4 import BeautifulSoup
import pandas as pd
import re
import wikipedia


# cleans artist's names scrapped from billboard by only keeping the first artist in cases of collaborations. Ignores all featuring artists.  
def clean_name(artist_name):
    word_list = []
    name=0
    for word in artist_name.split():
        if word.lower() =='featuring' or word.lower()=='x' or word.lower()=='(' or word.lower()=='[' or word.lower() == 'with' or word.lower() == 'duet' or word.lower() == '&':
            return name

        word_list.append(word)
        name = " ".join(word_list)
    return name

# scrapes top 100  billboard songs of a given year 
def scrape_billboard_top100(year):
    # general url of top 100
    url = 'https://www.billboard.com/charts/year-end/' + str(year) + '/hot-100-songs'
    response = requests.get(url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    # container with song information
    song_containers = html_soup.find_all('div', class_ = 'ye-chart-item__text')
    rank_containers = html_soup.find_all('div', class_ = 'ye-chart-item__rank')
    # list of tuples of top 100 artists
    top100 = []
    # for each of the top 100
    for i in range(len(song_containers)):

        song_info = song_containers[i]
        rank_info = rank_containers[i]
        # getting title of song 
        title_container = song_info.find('div', class_ = 'ye-chart-item__title')
        title = title_container.text[1:-1]
        # getting artist name 
        artist_container = song_info.find('div', class_ = 'ye-chart-item__artist')
        rank = rank_info.text[1:-1]
        rank = int(rank)
        # extracting artist name from scraped container
        artist_dirty = artist_container.text[1:-1]
        # removing escape sequences from artist's name
        artist_dirty = artist_dirty.replace('\n', '')
        artist_dirty = artist_dirty.replace('\t', '')
        artist = clean_name(artist_dirty)
        # removing whitespace before and after name
        artist = artist.lstrip()
        artist = artist.rstrip()
        
        # artist name doesn't match with billboard's name 
        if artist == "Soulja Boy Tell'em":
            artist = 'Soulja Boy'

        # top 100 information 
        top100.append((title, artist, rank))

    return(top100)

# scrape AZlyrics.com for music lyrics given song and artist
def scrape_lyrics(artist, song):

    USER_AGENTS = [
            'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
            'Mozilla/5.0 (iPad; CPU OS 8_4_1 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12H321 Safari/600.1.4',
            'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
            'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36']

    # search for lyrics
    url = 'https://search.azlyrics.com/search.php?q=' + str(artist) + '+' +  str(song)
    content_html = requests.get(url, headers={'User-Agent': random.choice(USER_AGENTS)})
    html_soup = BeautifulSoup(content_html.text, 'html.parser')
    # first search result 
    first_result_container = html_soup.find_all('td', class_ = 'text-left visitedlyr')[0]
    # get the first result of the search
    lyrics_link = first_result_container.find_all('a')[0].get('href')
    html_lyrics = requests.get(lyrics_link,headers={'User-Agent': random.choice(USER_AGENTS)})
    html_lyrics_soup = BeautifulSoup(html_lyrics.text, 'html.parser')
    lyrics = str(html_lyrics_soup)
    # lyrics lies between up_partition and down_partition
    up_partition = '<!-- Usage of azlyrics.com content by any third-party lyrics provider is prohibited by our licensing agreement. Sorry about that. -->'
    down_partition = '<!-- MxM banner -->'
    lyrics = lyrics.split(up_partition)[1]
    lyrics = lyrics.split(down_partition)[0]
    lyrics = lyrics.replace('<br>','').replace('</br>','').replace('</div>','').replace('<br/>','').replace('<i>','').replace('</i>','').replace('\n',' ').strip()
    lyrics = html.unescape(lyrics)
    lyrics = re.sub('\s?\[[\w\s\-\&\$\d\(\)]+\:\]\s','',lyrics)
    lyrics = re.sub('[^A-Za-z0-9\s]+', "", lyrics)
    lyrics = lyrics.replace('\n', '')
    lyrics = lyrics.replace('\t', '')
    lyrics = lyrics.replace('\r', '')

    return lyrics


def create_dataset():

    for year in [2008, 2018]:

        all_lyrics = []
        available_artists = []
        available_titles = []
        ranks= []
        years = []

        print(year)
        # get top100 billboard information
        top100 = scrape_billboard_top100(year)
        # iterating over information of each of the top100 songs
        for song_details in top100:
            # title of song
            title = song_details[0]
            # artist name
            artist = song_details[1]
            # billboard rank of song 
            rank = song_details[3]
            
            try:
                lyrics = scrapers.scrape_lyrics(artist, title)
                all_lyrics.append(lyrics)
                available_artists.append(artist)
                available_titles.append(title)
                ranks.append(rank)
                years.append(year)

            except:
                print('Could not get lyrics for ', artist)
                
            time.sleep(8)

        data = pd.DataFrame(columns=['Song', 'Artist', 'Lyrics', 'Rank', 'Year'])
        data['Artist'] = available_artists
        data['Song'] = available_titles
        data['Year'] = years
        data['Rank'] = ranks
        data['Lyrics'] = all_lyrics
        data['Lyrics'] = data['Lyrics'].apply(lambda x: x.replace('\r', ''))
        
        filename = 'data/billboard_top100_' + str(year) + '.csv'
        data.to_csv(filename, index=False)
