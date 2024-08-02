import feedparser
import requests
from requests.exceptions import SSLError, RequestException
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import logging
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_final_url(url):
    try:
        response = requests.get(url, allow_redirects=True)
        return response.url
    except SSLError:
        logger.error(f"SSL Error for URL: {url}. Skipping...")
        return None
    except RequestException:
        logger.error(f"Connection error for URL: {url}. Skipping...")
        return None

def get_final_url_selenium(url):
    chromedriver_autoinstaller.install()

    options = Options()
    options.headless = True
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    
    try:
        logger.info(f"Acessando a URL: {url}")
        driver.set_page_load_timeout(60)
        driver.get(url)
        
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        
        initial_url = driver.current_url
        max_attempts = 10
        attempts = 0
        while driver.current_url == initial_url and attempts < max_attempts:
            logger.info(f"Esperando redirecionamento... Tentativa {attempts + 1}")
            time.sleep(1)
            attempts += 1
        
        final_url = driver.current_url
        if final_url == initial_url:
            logger.warning("A URL não mudou após o redirecionamento.")
        
        logger.info(f"URL final obtida: {final_url}")
        return final_url
    except Exception as e:
        logger.error(f"Erro ao acessar a URL: {e}")
        return None
    finally:
        driver.quit()

def get_thumbnail_url(final_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(final_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
        
        twitter_image = soup.find('meta', name='twitter:image')
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
        
        img_tag = soup.find('img')
        if img_tag and img_tag.get('src'):
            return img_tag['src']
        
        return None
    except requests.exceptions.HTTPError as http_err:
        logger.error(f"Erro HTTP ao obter a URL da miniatura: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logger.error(f"Erro de requisição ao obter a URL da miniatura: {req_err}")
    except Exception as e:
        logger.error(f"Erro ao obter a URL da miniatura: {e}")
    return None

def fetch_news_thumbnails(rss_url, limit=None):
    feed = feedparser.parse(rss_url)
    news = []
    redirect_domains = ['news.google.com']

    for i, entry in enumerate(feed.entries):
        if limit is not None and i >= limit:
            break
        article_title = entry.title
        article_url = entry.link
        if hasattr(entry, 'published'):
            article_pub_date = entry.published
        else:
            article_pub_date = None
        
        if any(domain in article_url for domain in redirect_domains):
            final_url = get_final_url_selenium(article_url)
        else:
            final_url = get_final_url(article_url)
        
        if final_url is None:
            continue
        thumbnail_url = get_thumbnail_url(final_url)
        if thumbnail_url:
            news.append({'article_title': article_title, 'article_url': final_url, 'thumbnail_url': thumbnail_url, 'article_pubdate': article_pub_date})
    return news