from typing import List

class NewsService:
    def __init__(self, *, ai_service, supabase_service, whatsapp_service):
        self.ai_service = ai_service
        self.supabase_service = supabase_service
        self.whatsapp_service = whatsapp_service

    def get_news_sources(self, project_id):
        query = f"project_id=eq.{project_id}&active=eq.true&select=*"
        return self.supabase_service.select_data("news_source", query)
    
    def delete_news_by_project(self, project_id):
        query = f"project_id=eq.{project_id}"
        return self.supabase_service.delete_data("news", query)
    
    def get_recent_news(self, project_id, limit_last_chosen_news=50):
        return self.supabase_service.select_data('news_chosen', f'order=id.desc&limit={limit_last_chosen_news}&project_id=eq.{project_id}')

    def choose_news(self, all_news: List[dict], recent_news, prompt: str, ai: str, model: str, max_tokens: int = 100, limit_choose_news: int = 4, limit_last_chosen_news: int = 50) -> List[dict]:        
        recent_news_url = ', '.join([news['url'] for news in recent_news])

        prompt = prompt.format(limit_choose_news=limit_choose_news, recent_news_url=recent_news_url)

        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": ", ".join([news['url'] for news in all_news])
            }
        ]
 

        chosen_urls = self.ai_service.generate_text(messages, ai, model, max_tokens)

        news_chosen = [news for news in all_news if news['url'] in chosen_urls]
        self.supabase_service.insert_data('news_chosen', news_chosen)

        return news_chosen
    
    def inital_introduction(self, prompt, ai, model, max_tokens=100):
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": ""
            }
        ]
        introduction = self.ai_service.generate_text(messages, ai, model, max_tokens)
        return introduction
            
    
    def create_headline(self, chosen_news, prompt, ai, model, max_tokens=100):        
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": ", ".join([news['url'] for news in chosen_news])
            }
        ]
        headline = self.ai_service.generate_text(messages, ai, model, max_tokens)
        return headline

    def summarize_news(self, news_url, prompt, ai, model, max_tokens=100):
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": news_url
            }
        ]
        summary = self.ai_service.generate_text(messages, ai, model, max_tokens)
        return summary

    def get_subscribers(self, project_id: str):
        query = f"project_id=eq.{project_id}&active=eq.true"
        return self.supabase_service.select_data("news_subscribers", query)

    def send_headline_news(self, number: str, headline: str):
        response, status_code = self.whatsapp_service.send_text_message_whatsapp(number, headline)
        if status_code == 201:
            if response.get('error'):
                print("Erro ao enviar a mensagem:", response.get('error'))
            else:
                print("Mensagem enviada com sucesso.")
        else:
            print(f"Erro na requisição: Código de status {status_code}")
    
    def send_introduction(self, number: str, introduction: str):
        response, status_code = self.whatsapp_service.send_text_message_whatsapp(number, introduction)
        if status_code == 201:
            if response.get('error'):
                print("Erro ao enviar a mensagem:", response.get('error'))
            else:
                print("Mensagem enviada com sucesso.")
        else:
            print(f"Erro na requisição: Código de status {status_code}")
    
    def send_image_news(self, number: str, image_url: str, caption: str):
        response, status_code = self.whatsapp_service.send_media_url_whatsapp(number, image_url, caption)
        if status_code == 201:
            if response.get('error'):
                print("Erro ao enviar a mensagem:", response.get('error'))
            else:
                print("Mensagem enviada com sucesso.")
        else:
            print(f"Erro na requisição: Código de status {status_code}")

    def load_excluded_domains(self, project_id):
        query = f"project_id=eq.{project_id}&select=domain"
        excluded_domains = self.supabase_service.select_data("news_excluded_domains", query)
        return [domain['domain'] for domain in excluded_domains]
    
    def load_project_details_with_prompts(self, project_id):
        query = (
            f"id=eq.{project_id}&"
            "select=id,"
            "name,"
            "choose_news_prompt:choose_news_prompt_id!inner(id,description),"
            "create_headline_prompt:create_headline_prompt_id!inner(id,description),"
            "summarize_news_prompt:summarize_news_prompt_id!inner(id,description),"
            "introduction_prompt:introduction_prompt_id!inner(id,description)"
        )
        project_details = self.supabase_service.select_data("news_projects", query)
        return project_details[0] if project_details else None