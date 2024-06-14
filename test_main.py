from re import T
import unittest
import json
from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
from news_service import NewsService
from whatsapp_service import WhatsAppService
from evolution_service import EvolutionApiService # noqa: F401
from generic_ai_service import GenericAIService
class TestFunctions(unittest.TestCase):
    def setUp(self):
        # Load the configuration file
        with open("config.json") as config_file:
            config = json.load(config_file)


        # Get the configuration for the WhatsApp API service
        whatsapp_api_config = config["whatsapp"]["api_service"]

        # Get the service class name and remove it from the config
        service_class_name = whatsapp_api_config.pop("service_class_name")

        # Remove the instance_name from the config
        # instance_name = whatsapp_api_config.pop("instance_name", None)

        # Get a reference to the service class by name
        service_class = globals()[service_class_name]

        # Now whatsapp_api_config doesn't contain 'service_class_name' and 'instance_name', so it can be passed to the service class constructor
        whatssapp_api_service = service_class(whatsapp_api_config)

        # Create the service instances
        ai_service = GenericAIService()
        self.supabase_service = SupabaseService(config["database"]["supabase"]["url"], config["database"]["supabase"]["key"])
        whatsapp_service = WhatsAppService(api_service=whatssapp_api_service)

        self.news_service = NewsService(ai_service=ai_service, supabase_service=self.supabase_service, whatsapp_service=whatsapp_service)
        self.rss_url = "https://news.google.com/rss/search?q=financial%20market%20canada%20when%3A1d&hl=en-CA&gl=CA&ceid=CA%3Aen"

    def test_fetch_news_thumbnails(self):
        limit = 10
        news = fetch_news_thumbnails(self.rss_url, limit)
        self.assertLessEqual(len(news), limit)

    def test_insert_data(self):
        data = {
            'title': 'test_title',
            'url': 'test_url',
            'image': 'test_image',
            'published': 'test_published',
            'project_id': '1'
        }
        status_code = self.supabase_service.insert_data('news', data)
        assert status_code == 201

    def test_choose_news(self):
        all_news = [{'source': 'test_source', 'title': 'test_title', 'url': 'test_url'}]
        ai = 'groq'
        model = 'llama3-70b-8192'
        max_tokens = 100
        chosen_news = self.news_service.choose_news(all_news, ai, model, max_tokens)
        self.assertIsInstance(chosen_news, list)  # Verify that the response is a list
        #self.assertEqual(chosen_news, True)  # Adjust this based on your AI's behavior
        #self.assertEqual(chosen_news, all_news)  # Adjust this based on your AI's behavior

    def test_get_news_sources(self):
        project_id = 1
        news_sources = self.supabase_service.get_news_sources(project_id)
        self.assertIsInstance(news_sources, list)


if __name__ == '__main__':
    unittest.main()