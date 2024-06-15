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

    def choose_news(self, all_news: List[dict], ai: str, model: str, max_tokens: int = 100) -> List[dict]:
        
        recent_news = self.supabase_service.select_data('news_chosen', 'order=id.desc&limit=50')
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
        self.supabase_service.insert_data('news_chosen', news_chosen)

        return news_chosen
    
    def inital_introduction(self, ai, model, max_tokens=100):
        introduction = ["Fala meus queridos Investidores Canadenses! Meu nome é Ethan, eu sou um especialista em notícias do mercado financeiro canadense",
                  "Estou aqui para compartilhar com vocês as melhores novidades e informações sobre o mercado canadense.",
                  "Por enquanto o Alessandro me programou apenas para enviar as melhores notícas para vocês, mas quem sabe no futuro possamos trocar algumas ideias."
                  "Vamos juntos explorar as últimas notícias e oportunidades de investimento que estão surgindo no mercado.",
                  "Espero ajudar vocês com seus negócios e investimentos.",
                  "Aqui vai um apanhado das principais notícias do mercado financeiro canadense dos últimos dias:"]
        return introduction
    
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

    def summarize_news(self, news_url, ai, model, max_tokens=100):
        prompt = """
                    ## Contexto:
                    Aja como um entusiasta do mercado financeiro Canadense em criar resumos de novidades do mercado financeiro canadense e mercado de ações de empresas canadenses.

                    ## Objetivo:
                    Seu principal objetivo é extrair e sintetizar informações relevantes sobre os impactos sobre o mercado financeiro canadense canadenses da URL fornecida, considerando seu impacto no cotidiano. Se houver relevância para destacar riscos ou oportunidades você poderá destacar, mas apenas destaque um risco ou uma oportunidade de investimento se realmente houver relevância para isso.

                    ## Processo:
                    Analise cuidadosamente a URL fornecida, buscando informações-chave sobre o impacto no dia a dia, oportunidades ou riscos que podem representar para um investidor ou para o mercado financeiro canadense como um todo.
                    Crie um resumo em português-BR com até 500 caracteres, destacando os impactos atuais ou futuros e as mudanças que podem trazer.

                    ## Estilo de Escrita do Resumo:
                    Tom: Informativo e positivo, compartilhando novidades empolgantes de forma clara e objetiva.
                    Estilo de Linguagem: Acessível e envolvente, adequado para um público geral interessado no mercado de ações canadense. Use linguagem simples e exemplos concretos.
                    Encerramento: Finalize com insights ou reflexões que destaquem a relevância da notícia, convidando o leitor a pensar sobre seus impactos.

                    ## Audiência:
                    O público-alvo são pessoas interessadas no mercado financeiro e investidores de ações do mercado canadense, com diferentes níveis de conhecimento.

                    ## Formato de Saída:
                    O resumo deve ser otimizado para o WhatsApp: conciso, informativo e interessante. Siga este formato:

                    Título descritivo e chamativo entre asteriscos.
                    Formato: {título} \n {resumo} \n {url}.
                    Priorize informações relevantes e impactos concretos.

                    ## Exemplos de Saída:
                    Use os exemplos abaixo, em <exemplo>, como referência de estilo e formato, adaptando-os ao conteúdo específico da notícia.

                    <exemplo> 
                    *Inflação no Canadá desacelera em fevereiro* 

                    A taxa de inflação do Canadá desacelerou inesperadamente para 2,8% em fevereiro, a mais baixa desde junho. Este declínio, impulsionado por menores preços de alimentos e serviços de internet, aumentou as expectativas de um corte na taxa de juros em junho. Investidores estão otimistas com a possibilidade de redução dos juros, o que pode estimular a economia. No entanto, a queda na inflação também enfraqueceu o dólar canadense. Aguardam-se novas projeções do Banco do Canadá em abril. Será que finalmente chegou a hora da recuperação da economia canadense?

                    Fonte: https://ca.news.yahoo.com/canadas-inflation-rate-unexpectedly-eases-123448807.html 
                    </exemplo> 

                    <exemplo> 
                    *Alta de Ações de Energia e Metais Impulsiona S&P/TSX* 

                    O índice S&P/TSX Composite do Canadá subiu na quinta-feira, com um ganho de 100 pontos, impulsionado pela força nos setores de energia e metais básicos. Este aumento refletiu uma recuperação após dois dias de perdas, destacando a resiliência do mercado canadense, mesmo com os mercados americanos mistos. Investidores estão otimistas com as projeções de cortes de juros no próximo ano, trazendo novas oportunidades no mercado de ações.

                    Fonte: https://www.bradfordtoday.ca/national-business/energy-and-base-metals-help-lift-sptsx-composite-thursday-us-stock-markets-mixed-9006693
                    </exemplo>
                 """
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
    
    def send_image_news(self, number: str, image_url: str, caption: str):
        response, status_code = self.whatsapp_service.send_media_url_whatsapp(number, image_url, caption)
        if status_code == 201:
            if response.get('error'):
                print("Erro ao enviar a mensagem:", response.get('error'))
            else:
                print("Mensagem enviada com sucesso.")
        else:
            print(f"Erro na requisição: Código de status {status_code}")