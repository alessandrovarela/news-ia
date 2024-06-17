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
    
    def load_project_config(self, project_id):
        query = (
            f"id=eq.{project_id}&"
            "select=id,"
            "name,"
            "config_json,"
            "choose_news_prompt:choose_news_prompt_id!inner(id,description),"
            "create_headline_prompt:create_headline_prompt_id!inner(id,description),"
            "summarize_news_prompt:summarize_news_prompt_id!inner(id,description),"
            "introduction_prompt:introduction_prompt_id!inner(id,description)"
        )
        project_config = self.select_data("news_projects", query)
        return project_config[0] if project_config else None