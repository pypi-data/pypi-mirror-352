from bs4 import BeautifulSoup
import requests



def get_soup(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    return soup



def get_lyrics(url):
    soup = get_soup(url)
    lyrics = soup.find("div", {"class": "song-text"}).text
    return lyrics