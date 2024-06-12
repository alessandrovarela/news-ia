from re import T
import unittest
import json
from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService
from news_service import NewsService  # Make sure to import NewsService
class TestFunctions(unittest.TestCase):
    def setUp(self):
        with open('config.json') as f:
            config = json.load(f)
        self.supabase_service = SupabaseService(config['database']['supabase']['url'], config['database']['supabase']['key'])
        self.news_service = NewsService(config['database']['supabase']['url'], config['database']['supabase']['key'])
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