from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
from news_service import NewsService
from whatsapp_service import WhatsAppService
from evolution_service import EvolutionApiService # noqa: F401
import json

# Load the configuration file
with open("config.json") as config_file:
    config = json.load(config_file)


# Create the Supabase service using the values from the configuration file
supabase_service = SupabaseService(config["database"]["supabase"]["url"], config["database"]["supabase"]["key"])
news_service = NewsService(config['database']['supabase']['url'], config['database']['supabase']['key'])

# Get the configuration for the WhatsApp API service
whatsapp_api_config = config["whatsapp"]["api_service"]

# Get the service class name and remove it from the config
service_class_name = whatsapp_api_config.pop("service_class_name")

# Remove the instance_name from the config
instance_name = whatsapp_api_config.pop("instance_name", None)

# Add the delay parameters to the config
#whatsapp_api_config["delay_enabled"] = config["whatsapp"]["delay_enabled"]
#whatsapp_api_config["average_char_min"] = config["whatsapp"]["average_char_min"]

# Get a reference to the service class by name
service_class = globals()[service_class_name]

# Now whatsapp_api_config doesn't contain 'service_class_name' and 'instance_name', so it can be passed to the service class constructor
api_service = service_class(whatsapp_api_config)

# Create the WhatsApp service using the API service
whatsapp_service = WhatsAppService(api_service=api_service)

supabase_service.delete_news_by_project(1)

news_sources = supabase_service.get_news_sources(1)
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


