
import argparse
from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
from news_service import NewsService
from whatsapp_service import WhatsAppService
from evolution_service import EvolutionApiService # noqa: F401
from generic_ai_service import GenericAIService
import json

parser = argparse.ArgumentParser(description='Process some integers.')

# Adiciona o argumento --project_id ao analisador
parser.add_argument('--project_id', type=int, help='An integer for the project ID')

# Analisa os argumentos de linha de comando
args = parser.parse_args()

# Usa o PROJECT_ID fornecido nos argumentos, ou um valor padrão se não for fornecido
PROJECT_ID = args.project_id if args.project_id is not None else 1

# Load the configuration file
with open("config.json") as config_file:
    config_file = json.load(config_file)

supabase_service = SupabaseService(config_file["database"]["supabase"]["url"], config_file["database"]["supabase"]["key"])
project_config = supabase_service.load_project_config(PROJECT_ID)
config = project_config['config_json']

whatsapp_api_config = config["whatsapp"]["api_service"]
service_class_name = whatsapp_api_config.pop("service_class_name", None)
service_class = globals()[service_class_name]
whatsapp_api_service = service_class(whatsapp_api_config)

# Create the service instances
ai_service = GenericAIService(config['ai'])

whatsapp_service = WhatsAppService(api_service=whatsapp_api_service)
news_service = NewsService(ai_service=ai_service, supabase_service=supabase_service, whatsapp_service=whatsapp_service)


news_service.delete_news_by_project(PROJECT_ID)
news_sources = news_service.get_news_sources(PROJECT_ID)

all_news = []

excluded_domains = news_service.load_excluded_domains(PROJECT_ID)

choose_news_prompt_description = project_config['choose_news_prompt']['description']
create_headline_prompt_description = project_config['create_headline_prompt']['description']
summarize_news_prompt_description = project_config['summarize_news_prompt']['description']
introduction_prompt = project_config['introduction_prompt']['description']

for source in news_sources:
    news = fetch_news_thumbnails(source['source'], source.get('limit'))

    filtered_news = [
        item for item in news
        if not any(domain in item['article_url'] for domain in excluded_domains)
    ]

    for item in filtered_news:
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


ai_choose_news_config = config['app']['ai_choose_news']
recent_news = news_service.get_recent_news(PROJECT_ID, ai_choose_news_config['limit_last_chosen_news'])

if not recent_news:
    send_introduction = True
else:
    send_introduction = False

# Get the AI choose news configuration
chosen_news = news_service.choose_news(
    all_news,
    recent_news,
    choose_news_prompt_description,
    ai_choose_news_config['ai'], 
    ai_choose_news_config['model'], 
    ai_choose_news_config['max_tokens'],
    ai_choose_news_config['limit_choose_news']
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
ai_create_headline_config = config['app']['ai_create_headline']
headline = news_service.create_headline(
    chosen_news,
    create_headline_prompt_description, 
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
    summarize_news_prompt_description, 
    ai_summarize_news_config['ai'], 
    ai_summarize_news_config['model'], 
    ai_summarize_news_config['max_tokens']
    )
    news['summary'] = summary


# Send newsletter para WhatsApp
# Send Headline
subscribers = news_service.get_subscribers(PROJECT_ID)

print("-------------> Sending news to subscribers: <-----------------")
for subscriber in subscribers:
    introduction = None
    if send_introduction:
        if not introduction:
            ai_inital_introduction_config = config['app']['ai_inital_introduction']
            introduction = news_service.inital_introduction(introduction_prompt, ai_inital_introduction_config['ai'], ai_inital_introduction_config['model'], ai_inital_introduction_config['max_tokens'])

        print(f"Sending introduction: number:{subscriber['number']}, introduction:{introduction}")
        news_service.send_introduction(subscriber['number'], introduction)

    print('---------------------------------------------------------')
    print(f"Headline: {headline}")
    news_service.send_headline_news(subscriber['number'], headline)

    for news in chosen_news:
        print(f"Sending news: number:{subscriber['number']}, image:{news['image']}, summary:{news['summary']}")
        news_service.send_image_news(subscriber['number'], news['image'], news['summary'])

    print('---------------------------------------------------------')

