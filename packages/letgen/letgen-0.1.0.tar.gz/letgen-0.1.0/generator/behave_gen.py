from rich import print
from .base import BaseGenerator


class BehaveGenerator(BaseGenerator):
    """Gerador de testes para o framework Behave."""
    
    def build_prompt(self, descricao):
        return f"""
Você é um especialista em automação de testes BDD com Behave em Python. Gere um conjunto completo de arquivos para testar o seguinte cenário: {descricao}

Por favor, forneça os seguintes arquivos, cada um em um bloco de código separado com a linguagem apropriada:

1. Um arquivo .feature com cenários BDD claros e bem estruturados
   - Use a sintaxe Gherkin correta (Feature, Scenario, Given, When, Then)
   - Inclua tags relevantes (@web, @mobile, @api, etc.)
   - Adicione descrições claras para a Feature e Scenarios
   - Use exemplos (Scenario Outline) quando apropriado
   - Mantenha os passos concisos e focados em comportamento, não em implementação

2. Um arquivo de steps em Python que implementa os passos definidos no arquivo .feature
   - Implemente todos os passos mencionados no arquivo .feature
   - Use decoradores @given, @when, @then corretamente
   - Inclua tratamento de erros e validações
   - Use padrões de expressão regular para tornar os passos reutilizáveis
   - Importe e use o Page Object Model

3. Um arquivo de Page Object Model em Python para encapsular as interações com a interface
   - Crie classes para cada página ou componente principal
   - Implemente métodos para cada ação possível na interface
   - Inclua localizadores de elementos (CSS, XPath, ID, etc.)
   - Adicione métodos de espera e verificação
   - Siga o princípio de encapsulamento (não exponha detalhes de implementação)

Cada arquivo deve seguir as melhores práticas de automação de testes, incluindo:
- Nomenclatura clara e descritiva seguindo convenções Python (snake_case para métodos e variáveis)
- Comentários explicativos onde necessário
- Estrutura modular e reutilizável
- Tratamento adequado de exceções e timeouts
- Asserções claras e significativas

Formate sua resposta EXATAMENTE da seguinte forma, mantendo os marcadores de código e linguagem:

```feature
# Conteúdo do arquivo .feature aqui
```

```python
# Conteúdo do arquivo de steps aqui
```

```python
# Conteúdo do arquivo de Page Object Model aqui
```

Certifique-se de que o código gerado seja funcional, completo e pronto para ser executado com o framework Behave.
        """
    
    # Usando o método call_groq_api da classe base BaseGenerator
    
    def format_output(self, response):
        try:
            # Tenta dividir a resposta em seções
            sections = response.split('```')
            
            # Extrai as seções relevantes
            feature_file = ""
            steps_file = ""
            page_object = ""
            
            # Processa as seções da resposta
            for i, section in enumerate(sections):
                if i > 0 and i < len(sections) - 1:  # Ignora o primeiro e último (que são texto explicativo)
                    # Identifica o tipo de seção pelo conteúdo ou cabeçalho
                    section_content = section.strip()
                    if section_content.startswith('feature') or '.feature' in section_content.lower():
                        feature_file = section.split('\n', 1)[1] if '\n' in section else section
                    elif section_content.startswith('python') and ('steps' in section_content.lower() or 'step_definitions' in section_content.lower()):
                        steps_file = section.split('\n', 1)[1] if '\n' in section else section
                    elif section_content.startswith('python') and ('page' in section_content.lower() or 'pom' in section_content.lower()):
                        page_object = section.split('\n', 1)[1] if '\n' in section else section
            
            # Verifica se conseguimos extrair as seções esperadas
            if not feature_file and not steps_file and not page_object:
                # Tenta uma abordagem alternativa para extrair as seções
                # Procura por marcadores específicos que podem indicar o início de cada seção
                if '# Feature File' in response:
                    parts = response.split('# Feature File', 1)[1].split('#', 1)
                    if parts:
                        feature_file = parts[0].strip()
                
                if '# Steps File' in response:
                    parts = response.split('# Steps File', 1)[1].split('#', 1)
                    if parts:
                        steps_file = parts[0].strip()
                
                if '# Page Object' in response:
                    parts = response.split('# Page Object', 1)[1].split('#', 1)
                    if parts:
                        page_object = parts[0].strip()
            
            # Exibe as seções formatadas com cabeçalhos mais descritivos
            print("\n[bold green]Feature File (Behave BDD):[/bold green]")
            print(f"[cyan]{feature_file}[/cyan]")
            
            print("\n[bold green]Steps File (Python Implementation):[/bold green]")
            print(f"[cyan]{steps_file}[/cyan]")
            
            print("\n[bold green]Page Object Model (Python):[/bold green]")
            print(f"[cyan]{page_object}[/cyan]")
            
            # Adiciona uma nota sobre como usar os arquivos gerados
            print("\n[bold yellow]Instruções de Uso:[/bold yellow]")
            print("[white]1. Salve o Feature File com extensão .feature em uma pasta 'features'[/white]")
            print("[white]2. Salve o Steps File como steps.py em uma pasta 'features/steps'[/white]")
            print("[white]3. Salve o Page Object como pages.py em uma pasta 'features/pages'[/white]")
            print("[white]4. Execute com o comando: behave features/seu_arquivo.feature[/white]")
            
        except Exception as e:
            # Fallback para exibição simples em caso de erro no processamento
            print("\n[bold red]Não foi possível processar a resposta em seções:[/bold red]")
            print(f"[yellow]{response}[/yellow]")
            print(f"\n[bold red]Erro: {str(e)}[/bold red]")



# Instância para uso direto
behave_generator = BehaveGenerator()
