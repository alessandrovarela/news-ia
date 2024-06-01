import requests

class SupabaseService:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }

    def insert_data(self, table_name, data):
        response = requests.post(f"{self.base_url}/{table_name}", headers=self.headers, json=data)
        return response.status_code

    
    def select_data(self, table_name, query):
        response = requests.get(f"{self.base_url}/{table_name}?{query}", headers=self.headers)
        response.raise_for_status()  # Raise exception if the request failed
        return response.json()
    
    def delete_data(self, table_name, query):
        response = requests.delete(f"{self.base_url}/{table_name}?{query}", headers=self.headers)
        response.raise_for_status()  # Raise exception if the request failed
        return response.status_code

    def get_news_sources(self, project_id):
        query = f"project_id=eq.{project_id}&active=eq.true&select=*"
        return self.select_data("news_source", query)
    
    def delete_news_by_project(self, project_id):
        query = f"project_id=eq.{project_id}"
        return self.delete_data("news", query)