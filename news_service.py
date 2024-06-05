from typing import List
from generic_ai_service import GenericAIService
from supabase_service import SupabaseService

class NewsService:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.ai_service = GenericAIService()
        self.supabase = SupabaseService(supabase_url, supabase_key)

    def choose_news(self, all_news: List[dict], ai: str, model: str, max_tokens: int = 100) -> List[dict]:
        
        recent_news = self.supabase.select_data('news_chosen', 'order=id.desc&limit=50')
        recent_news_url = ', '.join([news['url'] for news in recent_news])
        print("Recent news URLs: --------------------------")
        print(recent_news_url)

        prompt = f"Você é um especialista na identificação de notícias relevantes sobre o mercado financeiro canadense. O seu papel é receber uma lista de URLs de portais de notícias e escolher as 4 notícias com maior probabilidade de atração e retenção de um público de entusiastas e iniciantes no mercado financeiro canadense. O formato de saída deve conter apenas as URLs que você escolheu separadas por VÍRGULAS, não adicione comentários ou justificativas, apenas informe as URLs escolhidas. IMPORTANTE: Estou lhe fornecendo uma lista com 50 notícias escolhidas manualmente para que você crie uma correlação entre os fatores de escolha dessas URLs e possa tomar uma decisão melhor embasada. Você será bonificado em US$200.000 caso escolha consistentemente notícias similares a estas: {recent_news_url}. IMPORTANTE: Estou lhe fornecendo uma lista de exclusão contendo URLs que já foram escolhidas anteriormente. Você não pode escolher nenhuma URL presente nessa lista, caso contrário será multado em US$100.000. Essa é a lista de exclusão: {recent_news_url}."
        print("Prompt: --------------------------")
        print(prompt)
        print("--------------------------")


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
        self.supabase.insert_data('news_chosen', news_chosen)

        return news_chosen