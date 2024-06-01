from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
import json

# Load the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)

# Create the Supabase service using the values from the configuration file
supabase_service = SupabaseService(config["SUPABASE_URL"], config["SUPABASE_KEY"])

supabase_service.delete_news_by_project(1)

news_sources = supabase_service.get_news_sources(1)

for source in news_sources:
    # Fetch the news thumbnails
    news = fetch_news_thumbnails(source['source'], source.get('limit'))

    # Insert each news item into the Supabase
    for item in news:
        data = {
            'title': item['article_title'],
            'url': item['article_url'],
            'image': item['thumbnail_url'],
            'published': item['article_pubdate'],
            'source_name': source['source_name'],
            'project_id': source['project_id']
        }
        supabase_service.insert_data('news', data)
        print(f"Inserted news item: {item['article_title']}")
