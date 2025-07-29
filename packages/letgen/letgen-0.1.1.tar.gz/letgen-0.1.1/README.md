# 🧪 LetGen – Gerador de Cenários de Testes Automatizados com IA (Python)

[![PyPI version](https://badge.fury.io/py/letgen.svg)](https://badge.fury.io/py/letgen)
![Python version](https://img.shields.io/pypi/pyversions/letgen)
![License](https://img.shields.io/github/license/CarlossViniciuss/let)

LetGen é uma biblioteca Python para geração automatizada de testes, utilizando inteligência artificial (Groq API) para criar testes a partir de descrições em linguagem natural.

---

## 🚀 Por que usar o LetGen?

- ⏱️ **Economia de tempo**: Crie rapidamente a estrutura dos testes automatizados
- 💬 **Linguagem natural**: Descreva o cenário, o LetGen escreve o teste
- ⚙️ **Multiplos frameworks**: Suporte a Pytest, Playwright, Robot e Behave
- 🧠 **Boas práticas**: Geração de testes com POM e organização profissional
- 📚 **Didático**: Ótimo para iniciantes aprenderem como estruturar testes

---

## 📋 Requisitos

- Python 3.7+
- Chave da API Groq (https://console.groq.com/)
- Conexão com a internet

---

## 💻 Instalação

```bash
pip install letgen
```

## 🔧 Uso

Existem três formas de executar o projeto:

### 1. Usando o comando letgen (Recomendado)

Esta é a forma mais simples e recomendada após a instalação:

```bash
letgen
```

### 2. Usando o script run_let.py

Alternativa para execução direta do script:

```bash
# Torne o script executável (se ainda não estiver)
chmod +x run_let.py

# Execute o script
./run_let.py
```

### 3. Usando o módulo Python diretamente

```bash
python -m cli
```

## 🔄 Fluxo de Execução

Ao executar o Let, o programa irá:

1. Solicitar sua chave de API da Groq (na primeira execução)
2. Perguntar qual framework de teste você está usando (pytest, playwright, robot ou behave)
3. Pedir uma descrição dos cenários de teste que você deseja gerar
4. Gerar os testes e exibi-los no terminal

## 🧪 Frameworks Suportados

### Pytest

Framework de testes em Python, ideal para testes unitários e de integração.

**Exemplo de descrição:**
```
Teste de busca no Google que verifica se ao pesquisar por "Python" aparecem resultados relacionados à linguagem de programação. O teste deve abrir o Google, inserir o termo de busca, clicar no botão de pesquisa e verificar se os resultados contêm a palavra Python.
```

**Exemplo de saída:**

O Let gerará dois arquivos:

1. **test_google_search.py** - Arquivo de teste Pytest
```python
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from google_search_page import GoogleSearchPage

@pytest.fixture
def browser():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

def test_google_search_for_python(browser):
    # Arrange
    search_page = GoogleSearchPage(browser)
    search_term = "Python"
    
    # Act
    search_page.navigate()
    search_page.search(search_term)
    results = search_page.get_search_results()
    
    # Assert
    assert len(results) > 0, "Nenhum resultado de pesquisa encontrado"
    assert any(search_term.lower() in result.lower() for result in results), \
        f"Termo '{search_term}' não encontrado nos resultados"
```

2. **google_search_page.py** - Page Object Model
```python
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class GoogleSearchPage:
    def __init__(self, driver):
        self.driver = driver
        self.url = "https://www.google.com"
        self.search_box = (By.NAME, "q")
        self.search_button = (By.NAME, "btnK")
        self.results = (By.CSS_SELECTOR, "h3")
    
    def navigate(self):
        self.driver.get(self.url)
    
    def search(self, term):
        search_input = self.driver.find_element(*self.search_box)
        search_input.clear()
        search_input.send_keys(term)
        search_input.send_keys(Keys.RETURN)
    
    def get_search_results(self):
        result_elements = self.driver.find_elements(*self.results)
        return [element.text for element in result_elements]
```

### Playwright

Framework moderno para automação de navegadores web, com suporte para múltiplos navegadores.

**Exemplo de descrição:**
```
Teste de login em um site de e-commerce que verifica se um usuário pode fazer login com credenciais válidas. O teste deve navegar até a página de login, inserir nome de usuário e senha, clicar no botão de login e verificar se o usuário foi redirecionado para a página inicial com uma mensagem de boas-vindas.
```

### Behave (BDD)

Framework de BDD (Behavior-Driven Development) para Python.

**Exemplo de descrição:**
```
Cenário de teste para verificar o processo de checkout em um e-commerce. O usuário deve poder adicionar produtos ao carrinho, prosseguir para o checkout, preencher informações de envio e pagamento, e finalizar a compra com sucesso recebendo um número de pedido.
```

### Robot Framework

Framework genérico de automação de testes com sintaxe tabular.

**Exemplo de descrição:**
```
Teste para um aplicativo de lista de tarefas que verifica se o usuário pode adicionar uma nova tarefa, marcar como concluída e excluir a tarefa. O teste deve verificar se a tarefa aparece na lista após ser adicionada, se o status muda ao ser marcada como concluída e se a tarefa é removida da lista após ser excluída.
```

## 📝 Dicas de Uso

1. **Seja específico nas descrições**: Quanto mais detalhada for sua descrição, melhores serão os testes gerados.

2. **Mencione verificações**: Inclua na descrição quais verificações (assertions) você espera que sejam feitas.

3. **Descreva o fluxo completo**: Mencione todos os passos que o teste deve executar, desde a navegação inicial até as verificações finais.

4. **Adapte o código gerado**: O código gerado é um ponto de partida sólido, mas você pode precisar adaptá-lo às especificidades do seu projeto.

5. **Salve os arquivos gerados**: Copie e salve o código gerado em arquivos com os nomes sugeridos nas instruções de uso.

## 🔍 Solução de Problemas

### Erro na API da Groq

Se você encontrar erros relacionados à API da Groq:

1. Verifique se sua chave de API está correta
2. Confirme se você tem conexão com a internet
3. Verifique se a API da Groq está operacional
4. Se o erro persistir, tente novamente mais tarde

### Problemas com a Formatação da Saída

Se a saída não estiver formatada corretamente:

1. Verifique se você está usando uma versão recente do Python
2. Certifique-se de que todas as dependências estão instaladas
3. Tente uma descrição mais simples e depois aumente a complexidade

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

### Fluxo de Trabalho com Branches

Este projeto utiliza um fluxo de trabalho baseado em branches para desenvolvimento e testes:

1. **Branch `main`**: Contém o código estável e pronto para produção
2. **Branch `homolog`**: Ambiente de homologação para testar alterações antes de integrá-las à `main`

Para contribuir:

```bash
# Clone o repositório
git clone https://github.com/CarlossViniciuss/let.git
cd let

# Crie uma branch de feature a partir da homolog
git checkout homolog
git checkout -b feature/sua-feature

# Faça suas alterações e commit
git add .
git commit -m "Descrição da sua alteração"

# Envie para o repositório remoto
git push origin feature/sua-feature
```

Em seguida, abra um Pull Request para a branch `homolog`. Após testes e aprovação, as alterações serão mescladas na branch `main`.

## 📄 Licença

Este projeto está licenciado
