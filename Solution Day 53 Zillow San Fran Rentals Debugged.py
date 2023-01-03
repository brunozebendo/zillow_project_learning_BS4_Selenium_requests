""""O objetivo do site é pesquisar o preço de casas que atendam determinados critérios no site do Zillow,
então essa informação será transferida para um formulário criado no Google Sheets. No caso do projeto,
a pesquisa será feita para a cidade de São Francisco, por $ 3000 de aluguel, tendo pelo menos um quarto,
os critérios de filtro são incorporados no URL, depois será usado o Beatiful Soup para vasculhar
todo o código hmtl, então, será usado o selenium para preencher o formulário.
O primeiro passo é ir até o Google Forms e criar um formulário com 3 perguntas curtas,
depois copiar o url criado no programa.
Depois, ir até o site do Zillow e inspecionar os elementos para decidir como vai se obter o que se quer.
Então, usando Beatiful Soup, criar uma lista de nomes, preços e links dos imóveis encontrados.
Por fim, usando o Selenium, preencher o formulário do Google, e clicar no botão que cria a planilha (spreadsheet).
Dicas, para acessar o Zillow é preciso passar informações do header, conforme foi explicado no projeto da Amazon,
alguns links obtidos podem estar incompletos e se estiverem, devem ser completado com https://www.zillow.com,
Também é necessário pesquisar como pegar o último item de uma lista.
 As listagens com várias propriedades têm uma estrutura diferente das listagens com apenas uma única propriedade.
Use o Inspect Element do Chrome para verificar isso no site da Zillow.
Se todas as listagens estivessem usando a mesma classe CSS para armazenar as informações de preço, a solução
de 1ª passagem nos recursos do curso funcionaria. Veja se você pode usar uma estrutura try-except
(abordada no dia 30) para analisar a árvore com BeautifulSoup para lidar com os dois casos - descartando
o preço do título fornecido para várias listagens, bem como o preço/mês para listagens únicas."""

"""aqui as bibliotecas usadas, BeatifulSoup para trabalhar as informações, requests para requisitar as informações,
webdriver para trabalhar as informações e time"""
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
import time
"""header passa as informações do computador para o site, o que é exigido por alguns sites, mas não localizei como descobrir
se o site exige ou não e quais informações. As informações são obtidas no site que tem no material da aula 47"""
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}
"""aqui a variável guarda o resultado da consulta ao site já com os requisitos de pesquisa, é passado o url e o header"""
response = requests.get(
    "https://www.zillow.com/homes/San-Francisco,-CA_rb/?searchQueryState=%7B%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22San%20Francisco%2C%20CA%22%2C%22mapBounds%22%3A%7B%22west%22%3A-122.55177535009766%2C%22east%22%3A-122.31488264990234%2C%22south%22%3A37.69926912019228%2C%22north%22%3A37.851235694487485%7D%2C%22regionSelection%22%3A%5B%7B%22regionId%22%3A20330%2C%22regionType%22%3A6%7D%5D%2C%22isMapVisible%22%3Atrue%2C%22filterState%22%3A%7B%22fr%22%3A%7B%22value%22%3Atrue%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22pmf%22%3A%7B%22value%22%3Afalse%7D%2C%22pf%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A3000%7D%2C%22price%22%3A%7B%22max%22%3A872627%7D%2C%22beds%22%3A%7B%22min%22%3A1%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%7D",
    headers=header)
"""aqui, o site é transformado em texto e passado para a variável soup, para isso são passados os atributos padrões data
e html.parser"""
data = response.text
soup = BeautifulSoup(data, "html.parser")
"""então todos os elementos da classe abaixo são guardados em uma nova variável"""
all_link_elements = soup.select(".list-card-top a")
"""é criado um dicionário vazio que vai guardar o resultado do for loop que, por sua vez, vai iterar por todos
os elementos href, preencher os links incompletos e acrescentar (append) no dicionário"""
all_links = []
for link in all_link_elements:
    href = link["href"]
    print(href)
    if "http" not in href:
        all_links.append(f"https://www.zillow.com{href}")
    else:
        all_links.append(href)
"""primeiro, são selecionados todos os itens da classe abaixo e armazenados na variável, então, 
o list comprehension pega o endereço em forma de texto, divide e fica com o elemento antes do |, usando o [-1] para pegar
o último elemento (creio que para que fiquem na mesma ordem do link na planilha"""
all_address_elements = soup.select(".list-card-info address")
all_addresses = [address.get_text().split(" | ")[-1] for address in all_address_elements]
"""aqui, pelo que entendi o preço pode estar em diferentes listagem, então, é usado o try, except e o finally
para lidar com todas as possíveis classes onde o elemento pode estar"""
all_price_elements = soup.select(".list-card-heading")
all_prices = []
for element in all_price_elements:
    # Get the prices. Single and multiple listings have different tag & class structures
    try:
        # Price with only one listing
        price = element.select(".list-card-price")[0].contents[0]
    except IndexError:
        print('Multiple listings for the card')
        # Price with multiple listings
        price = element.select(".list-card-details li")[0].contents[0]
    finally:
        all_prices.append(price)

"""aqui começa a parte de preenchimento do formulário, primeiro o endereço do chrome_driver_path no computador
depois, é criada a variável driver (essa é a sintaxe padrão)"""
# Create Spreadsheet using Google Form
# Substitute your own path here 👇
chrome_driver_path = YOUR_PATH_HERE
driver = webdriver.Chrome(executable_path=chrome_driver_path)
"""aqui o for loop foi criado para guardar todos os dados, independentemente do comprimento da lista. Depois
tem que se passar o url do formulário google, espera dois segundos e depois achar cada elemento do formulário
pelo xpath, e depois o preencher, através do send_keys, com os dados dos dicionários acima criados.
 Reparar como o [n] já é suficiente para que se passe todos os dados, graças ao for loop...elegante...
 Por fim, o submit_button é clicado e cria um spreadsheet"""
for n in range(len(all_links)):
    # Substitute your own Google Form URL here 👇
    driver.get(URL_TO_YOUR_GOOGLE_FORM)

    time.sleep(2)
    address = driver.find_element_by_xpath(
        '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')
    price = driver.find_element_by_xpath(
        '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')
    link = driver.find_element_by_xpath(
        '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')
    submit_button = driver.find_element_by_xpath('//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div/div')

    address.send_keys(all_addresses[n])
    price.send_keys(all_prices[n])
    link.send_keys(all_links[n])
    submit_button.click()