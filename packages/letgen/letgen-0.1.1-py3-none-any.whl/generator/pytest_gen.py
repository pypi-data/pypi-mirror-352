from rich import print
from .base import BaseGenerator


class PytestGenerator(BaseGenerator):
    """Gerador de testes para o framework Pytest."""
    
    def build_prompt(self, descricao):
        return f"""
Você é um especialista em automação de testes com Pytest em Python. Gere um conjunto completo de arquivos para testar o seguinte cenário: {descricao}

Por favor, forneça os seguintes arquivos, cada um em um bloco de código separado com a linguagem apropriada:

1. Um arquivo de teste Pytest em Python com casos de teste bem estruturados
   - Siga a convenção de nomenclatura do Pytest (prefixo 'test_' para arquivos e funções)
   - Implemente testes que cubram todos os aspectos do cenário descrito
   - Use fixtures do Pytest para configuração e limpeza
   - Organize o código em funções de teste claras e bem nomeadas
   - Inclua verificações e asserções adequadas
   - Use parametrização para testar múltiplas condições quando apropriado
   - Adicione marcadores (markers) relevantes para categorizar os testes
   - Implemente tratamento de erros e timeouts
   - Use o Page Object Model para interações com a interface

2. Um arquivo de Page Object Model em Python para encapsular as interações com a interface (se aplicável)
   - Crie classes para cada página ou componente principal
   - Implemente métodos para cada ação possível na interface
   - Inclua localizadores de elementos (CSS, XPath, etc.)
   - Adicione métodos de espera e verificação
   - Siga o princípio de encapsulamento (não exponha detalhes de implementação)
   - Use tipos de retorno apropriados para cada método

Cada arquivo deve seguir as melhores práticas de automação de testes, incluindo:
- Uso adequado de fixtures e hooks do Pytest
- Nomenclatura clara e descritiva seguindo as convenções do Pytest
- Comentários explicativos onde necessário
- Estrutura modular e reutilizável
- Tratamento adequado de exceções e timeouts
- Asserções claras e significativas
- Uso de parametrização quando apropriado
- Documentação de funções e classes com docstrings

Formate sua resposta EXATAMENTE da seguinte forma, mantendo os marcadores de código e linguagem:

```python
# Conteúdo do arquivo de teste Pytest aqui
```

```python
# Conteúdo do arquivo de Page Object Model aqui (se aplicável)
```

Certifique-se de que o código gerado seja funcional, completo e pronto para ser executado com o Pytest.
        """
    
    # Usando o método call_groq_api da classe base BaseGenerator
    
    def format_output(self, response):
        try:
            # Tenta dividir a resposta em seções
            sections = response.split('```')
            
            # Extrai as seções relevantes
            test_file = ""
            page_object = ""
            
            # Processa as seções da resposta
            for i, section in enumerate(sections):
                if i > 0 and i < len(sections) - 1:  # Ignora o primeiro e último (que são texto explicativo)
                    # Identifica o tipo de seção pelo conteúdo ou cabeçalho
                    section_content = section.strip()
                    if section_content.startswith('python') and ("test" in section_content.lower() or "_test" in section_content.lower()):
                        test_file = section.split('\n', 1)[1] if '\n' in section else section
                    elif section_content.startswith('python') and ("page" in section_content.lower() or "pom" in section_content.lower()):
                        page_object = section.split('\n', 1)[1] if '\n' in section else section
            
            # Verifica se conseguimos extrair as seções esperadas
            if not test_file and not page_object:
                # Tenta uma abordagem alternativa para extrair as seções
                # Procura por marcadores específicos que podem indicar o início de cada seção
                if '# Test File' in response:
                    parts = response.split('# Test File', 1)[1].split('#', 1)
                    if parts:
                        test_file = parts[0].strip()
                
                if '# Page Object' in response:
                    parts = response.split('# Page Object', 1)[1].split('#', 1)
                    if parts:
                        page_object = parts[0].strip()
            
            # Exibe as seções formatadas com cabeçalhos mais descritivos
            print("\n[bold green]Pytest Test File (Python):[/bold green]")
            print(f"[cyan]{test_file}[/cyan]")
            
            print("\n[bold green]Page Object Model (Python):[/bold green]")
            print(f"[cyan]{page_object}[/cyan]")
            
            # Adiciona uma nota sobre como usar os arquivos gerados
            print("\n[bold yellow]Instruções de Uso:[/bold yellow]")
            print("[white]1. Salve o Test File como test_nome_do_teste.py[/white]")
            print("[white]2. Salve o Page Object como pages.py no mesmo diretório ou em uma pasta 'pages'[/white]")
            print("[white]3. Instale as dependências necessárias: pip install pytest selenium[/white]")
            print("[white]4. Execute com o comando: python -m pytest test_nome_do_teste.py -v[/white]")
            
        except Exception as e:
            # Fallback para exibição simples em caso de erro no processamento
            print("\n[bold red]Não foi possível processar a resposta em seções:[/bold red]")
            print(f"[yellow]{response}[/yellow]")
            print(f"\n[bold red]Erro: {str(e)}[/bold red]")



# Instância para uso direto
pytest_generator = PytestGenerator()