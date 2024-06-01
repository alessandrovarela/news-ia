import unittest
import json
from read_rss import fetch_news_thumbnails
from supabase_service import SupabaseService

class TestFunctions(unittest.TestCase):
    def setUp(self):
        with open('config.json') as f:
            config = json.load(f)
        self.supabase_service = SupabaseService(config['SUPABASE_URL'], config['SUPABASE_KEY'])
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

if __name__ == '__main__':
    unittest.main()