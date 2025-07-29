from rich import print
from .base import BaseGenerator


class RobotGenerator(BaseGenerator):
    """Gerador de testes para o framework Robot."""
    
    def build_prompt(self, descricao):
        return f"""
Você é um especialista em automação de testes com Robot Framework. Gere um conjunto completo de arquivos para testar o seguinte cenário: {descricao}

Por favor, forneça os seguintes arquivos, cada um em um bloco de código separado com a linguagem apropriada:

1. Um arquivo de teste Robot (.robot) com casos de teste bem estruturados
   - Use a sintaxe correta do Robot Framework
   - Organize o arquivo com as seções Settings, Variables, Test Cases e Keywords
   - Implemente casos de teste que cubram todos os aspectos do cenário descrito
   - Use tags para categorizar os testes
   - Adicione documentação para os casos de teste
   - Importe os recursos necessários
   - Use keywords de alto nível que descrevam o comportamento do teste

2. Um arquivo de recursos (.resource) com keywords personalizadas
   - Organize o arquivo com as seções Settings, Variables e Keywords
   - Implemente keywords reutilizáveis e bem nomeadas
   - Encapsule a lógica de interação com a interface
   - Importe as bibliotecas necessárias (SeleniumLibrary, etc.)
   - Defina variáveis para configuração
   - Implemente keywords para setup e teardown

3. Um arquivo de Page Object Model em Python para encapsular as interações com a interface (se aplicável)
   - Crie classes para cada página ou componente principal
   - Implemente métodos para cada ação possível na interface
   - Inclua localizadores de elementos
   - Adicione métodos de espera e verificação
   - Siga o princípio de encapsulamento

Cada arquivo deve seguir as melhores práticas de automação de testes, incluindo:
- Uso adequado da sintaxe e estrutura do Robot Framework
- Nomenclatura clara e descritiva seguindo as convenções do Robot Framework
- Comentários explicativos onde necessário
- Estrutura modular e reutilizável
- Tratamento adequado de exceções e timeouts
- Uso de tags e documentação
- Separação clara entre dados de teste, lógica de teste e interação com a interface

Formate sua resposta EXATAMENTE da seguinte forma, mantendo os marcadores de código e linguagem:

```robot
# Conteúdo do arquivo de teste Robot aqui
```

```robot
# Conteúdo do arquivo de recursos aqui
```

```python
# Conteúdo do arquivo de Page Object Model aqui (se aplicável)
```

Certifique-se de que o código gerado seja funcional, completo e pronto para ser executado com o Robot Framework.
        """
    
    # Usando o método call_groq_api da classe base BaseGenerator
    
    def format_output(self, response):
        try:
            # Tenta dividir a resposta em seções
            sections = response.split('```')
            
            # Extrai as seções relevantes
            test_file = ""
            resource_file = ""
            page_object = ""
            
            # Processa as seções da resposta
            for i, section in enumerate(sections):
                if i > 0 and i < len(sections) - 1:  # Ignora o primeiro e último (que são texto explicativo)
                    # Identifica o tipo de seção pelo conteúdo ou cabeçalho
                    section_content = section.strip()
                    if section_content.startswith('robot') and ("test" in section_content.lower() or ".robot" in section_content.lower()):
                        test_file = section.split('\n', 1)[1] if '\n' in section else section
                    elif section_content.startswith('robot') and ("resource" in section_content.lower() or ".resource" in section_content.lower()):
                        resource_file = section.split('\n', 1)[1] if '\n' in section else section
                    elif section_content.startswith('python') and ("page" in section_content.lower() or "pom" in section_content.lower()):
                        page_object = section.split('\n', 1)[1] if '\n' in section else section
            
            # Verifica se conseguimos extrair as seções esperadas
            if not test_file and not resource_file and not page_object:
                # Tenta uma abordagem alternativa para extrair as seções
                # Procura por marcadores específicos que podem indicar o início de cada seção
                if '# Test File' in response:
                    parts = response.split('# Test File', 1)[1].split('#', 1)
                    if parts:
                        test_file = parts[0].strip()
                
                if '# Resource File' in response:
                    parts = response.split('# Resource File', 1)[1].split('#', 1)
                    if parts:
                        resource_file = parts[0].strip()
                
                if '# Page Object' in response:
                    parts = response.split('# Page Object', 1)[1].split('#', 1)
                    if parts:
                        page_object = parts[0].strip()
            
            # Exibe as seções formatadas com cabeçalhos mais descritivos
            print("\n[bold green]Robot Test File (.robot):[/bold green]")
            print(f"[cyan]{test_file}[/cyan]")
            
            print("\n[bold green]Robot Resource File (.resource):[/bold green]")
            print(f"[cyan]{resource_file}[/cyan]")
            
            print("\n[bold green]Page Object Model (Python):[/bold green]")
            print(f"[cyan]{page_object}[/cyan]")
            
            # Adiciona uma nota sobre como usar os arquivos gerados
            print("\n[bold yellow]Instruções de Uso:[/bold yellow]")
            print("[white]1. Salve o Test File como nome_do_teste.robot[/white]")
            print("[white]2. Salve o Resource File como nome_do_recurso.resource[/white]")
            print("[white]3. Salve o Page Object como pages.py[/white]")
            print("[white]4. Instale o Robot Framework: pip install robotframework[/white]")
            print("[white]5. Execute com o comando: robot nome_do_teste.robot[/white]")
            
        except Exception as e:
            # Fallback para exibição simples em caso de erro no processamento
            print("\n[bold red]Não foi possível processar a resposta em seções:[/bold red]")
            print(f"[yellow]{response}[/yellow]")
            print(f"\n[bold red]Erro: {str(e)}[/bold red]")



# Instância para uso direto
robot_generator = RobotGenerator()