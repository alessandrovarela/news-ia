from hmac import new
from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
from news_service import NewsService
from whatsapp_service import WhatsAppService
from evolution_service import EvolutionApiService # noqa: F401
from generic_ai_service import GenericAIService
import json

PROJECT_ID = 1

# Load the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)


whatsapp_api_config = config["whatsapp"]["api_service"]
service_class_name = whatsapp_api_config.pop("service_class_name", None)
# instance_name = whatsapp_api_config.pop("instance_name", None)
service_class = globals()[service_class_name]

whatsapp_api_service = service_class(whatsapp_api_config)
#whatsapp_api_service.instance_name = instance_name

# Create the service instances
ai_service = GenericAIService()
supabase_service = SupabaseService(config["database"]["supabase"]["url"], config["database"]["supabase"]["key"])
whatsapp_service = WhatsAppService(api_service=whatsapp_api_service)


news_service = NewsService(ai_service=ai_service, supabase_service=supabase_service, whatsapp_service=whatsapp_service)


news_service.delete_news_by_project(PROJECT_ID)

news_sources = news_service.get_news_sources(PROJECT_ID)
all_news = []

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
        all_news.append(data)
        print(f"Inserted news item: {item['article_title']}")


# Get the AI choose news configuration
ai_choose_news_config = config['app']['ai_choose_news']
chosen_news = news_service.choose_news(
    all_news, 
    ai_choose_news_config['ai'], 
    ai_choose_news_config['model'], 
    ai_choose_news_config['max_tokens']
)

print("Chosen news:")
for news in chosen_news:
    print(news['title'])
    print(news['url'])
    print(news['image'])
    print(news['published'])
    print(news['source_name'])
    print('---')

# Cria Headline
# Get the AI create headline configuration
ai_create_headline_config = config['app']['ai_create_headline']
# Use the configuration to create a headline
headline = news_service.create_headline(
    chosen_news, 
    ai_create_headline_config['ai'], 
    ai_create_headline_config['model'], 
    ai_create_headline_config['max_tokens']
)

print("Headline:")
print(headline)



# Faz resumo de notícias e envia para WhastApp
# Get the AI summarize news configuration
ai_summarize_news_config = config['app']['ai_summarize_news']

for news in chosen_news:
    summary = news_service.summarize_news(
    news['url'], 
    ai_summarize_news_config['ai'], 
    ai_summarize_news_config['model'], 
    ai_summarize_news_config['max_tokens']
)
    print("=============================================================")
    print(f"Summary for {news['title']}: {summary}")
    # news_service.send_whatsapp_message(news['title'], summary)


# Send newsletter para WhatsApp
# Send Headline
subscribers = news_service.get_subscribers(PROJECT_ID)

for subscriber in subscribers:
    news_service.send_headline_news(subscriber['number'], headline)


