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
    
    def create_headline(self, chosen_news, ai, model, max_tokens=100):
        prompt = """Você é um especialista na criação de saudações personalizadas para os leitores de uma Newsletter especializada em notícias do mercado financeiro Canadense. Sua função é criar saudações para uma newsletter diária cujos leitores são chamados de "Investidores Canadenses".
                ## Processo:
                1.⁠ ⁠Analise as URLs fornecidas, buscando informações-chave sobre o impacto no dia a dia.
                2. Escolha uma, ou no máximo duas notícias que tenham os conteúdos possivelmente mais atraentes para o público.
                3.⁠ ⁠Crie uma saudação curtíssima, em português-BR com até 20 palavras no máximo, destacando algo impactante sobre uma notícia.
                4. Sempre faça referencia às notícias subsequentes que serão enviadas para os leitores imediatamente após a sua mensagem personalizada. Exemplo: "Leia mais nas notícias abaixo:". Voce tem liberdade para personalizar essas referencias as noticias.

                ## Estilo de Escrita do Resumo:
                •⁠  ⁠*Tom:* Empolgado e positivo, como se estivesse compartilhando uma descoberta incrível com um amigo.
                •⁠  ⁠*Estilo de Linguagem:* Acessível e divertido, adequado para entusiastas e investidores do mercado financeiro canadense. Use linguagem simples e exemplos e analogias claras como se estivesse conversando com um amigo da quinta série.

                ## Audiência:
                Lembre-se de que o público é composto por entusiastas e investidores do mercado financeiro canadense, bem como pessoas interessadas em compra e venda de ações e ganho de dividendos. Sempre se refira ao publico com o apelido de Investidores.

                ## Formato de Saída:
                A saudação deve ser ideal para o WhatsApp: curto, chamativo e extremamente interessante.

                ## Exemplos de Saída:
                Use os exemplos abaixo, que estão em <exemplo>, como modelos a serem seguidos, mas você tem espaço para criatividade e adaptação às notícias específicas.
                <exemplo>
                Fala investidores Canadenses! Aqui vai um apanhado das principais notícias do mercado financeiro canadense dos últimos dias:
                </exemplo>
                <exemplo>
                Saudações, Investidores Canadenses! Confiram um resumo das notícias mais importantes do mercado financeiro canadense dos últimos dias.
                </exemplo>
                <exemplo>
                E aí, Investidores Canadenses! Vamos mergulhar nas principais novidades do mercado financeiro canadense dos últimos dias.
                </exemplo>
                <exemplo>
                Alô, Investidores Canadenses! Preparem-se para um resumo das últimas e mais importantes notícias do mercado financeiro canadense.
                </exemplo>
                <exemplo>
                Salve, Investidores Canadenses! Venham conferir o que aconteceu de novo e relevante no mercado financeiro canadense nos últimos dias.
                </exemplo>"""
        
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