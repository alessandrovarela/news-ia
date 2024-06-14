import requests
from requests.exceptions import RequestException, SSLError

from bs4 import BeautifulSoup
import feedparser

def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        return response.url
    except SSLError:
        print(f"SSL Error for URL: {url}. Skipping...")
        return None
    except RequestException:
        print(f"Connection error for URL: {url}. Skipping...")
        return None

def get_thumbnail_url(final_url):
    response = requests.get(final_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    og_image = soup.find('meta', property='og:image')
    if og_image and og_image['content']:
        return og_image['content']
    return None

    # # Primeiro, tente pegar a imagem da meta tag og:image
    # og_image = soup.find('meta', attrs={'property': 'og:image'})
    # if og_image and og_image.get('content'):
    #     return og_image['content']
    
    # # Tente pegar a imagem da meta tag twitter:image
    # twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    # if twitter_image and twitter_image.get('content'):
    #     return twitter_image['content']
    
    # # Se não encontrar, procure por uma tag <img> comum
    # img_tag = soup.find('img')
    # if img_tag and img_tag.get('src'):
    #     return img_tag['src']
    
    # return None

def fetch_news_thumbnails(rss_url, limit=None):
    feed = feedparser.parse(rss_url)
    news = []
    for i, entry in enumerate(feed.entries):
        if limit is not None and i >= limit:
            break
        article_title = entry.title
        article_url = entry.link
        if hasattr(entry, 'published'):
            article_pub_date = entry.published
        else:
            article_pub_date = None  # or some default value

        final_url = get_final_url(article_url)
        
        if final_url is None:
            continue
        thumbnail_url = get_thumbnail_url(final_url)
        if thumbnail_url:
            news.append({'article_title': article_title, 'article_url': final_url, 'thumbnail_url': thumbnail_url, 'article_pubdate': article_pub_date})
    return news