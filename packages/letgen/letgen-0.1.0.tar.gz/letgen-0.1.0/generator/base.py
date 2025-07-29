from abc import ABC, abstractmethod
import requests

class BaseGenerator(ABC):
    """Interface comum para todos os geradores de testes."""
    
    @abstractmethod
    def build_prompt(self, descricao):
        """Constrói o prompt para a API da Groq."""
        pass
    
    def call_groq_api(self, api_key, prompt):
        """Chama a API da Groq com o prompt fornecido."""
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "llama3-70b-8192",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        try:
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except requests.exceptions.HTTPError as e:
            print(f"\n[bold red]Erro HTTP ao chamar a API da Groq: {e}[/bold red]")
            print(f"[yellow]Status Code: {e.response.status_code}[/yellow]")
            print(f"[yellow]Resposta: {e.response.text}[/yellow]")
            return f"Erro ao chamar a API da Groq: {str(e)}"
        except requests.exceptions.RequestException as e:
            print(f"\n[bold red]Erro de requisição ao chamar a API da Groq: {e}[/bold red]")
            return f"Erro ao chamar a API da Groq: {str(e)}"
        except KeyError as e:
            print(f"\n[bold red]Erro ao processar a resposta da API da Groq: {e}[/bold red]")
            print(f"[yellow]Resposta recebida: {response.json()}[/yellow]")
            return f"Erro ao processar a resposta da API da Groq: {str(e)}"
        except Exception as e:
            print(f"\n[bold red]Erro inesperado ao chamar a API da Groq: {e}[/bold red]")
            return f"Erro ao chamar a API da Groq: {str(e)}"
    
    @abstractmethod
    def format_output(self, response):
        """Formata a saída da API para exibição no terminal."""
        pass
    
    def generate(self, api_key, descricao):
        """Método principal que coordena a geração de testes."""
        prompt = self.build_prompt(descricao)
        response = self.call_groq_api(api_key, prompt)
        self.format_output(response)