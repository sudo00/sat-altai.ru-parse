import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import urllib.parse as urlparse
from urllib.parse import parse_qs


def perfomeTree(tree, category=''):
    treeDict = {}
    for li in tree:
        category = category + '/' + li.find('a').text
        liUl = li.find('ul')
        if (liUl):
            perfomeTree(liUl, category)
        else:
            response = requests.get(
                url='https://www.sat-altai.ru/catalog/?c=shop&category=' + li['id'] + '&clear=1&st=null',
                cookies=cookies
            )
            soup = BeautifulSoup(response.text, 'lxml')
            products = soup.find_all('a', {'class': 'product_name'})
            if products is None:
                continue

            for product in products:
                try:
                    productCode = ''
                    productName = ''
                    currPrice = ''
                    oldPrice = ''
                    sklad = ''
                    desc = ''
                    params = ''
                    params2 = ''
                    imgUrl = ''
                    productUrl = 'https://www.sat-altai.ru' + product['href']
                    response = requests.get(
                        url=productUrl,
                        cookies=cookies
                    )
                    soup = BeautifulSoup(response.text, 'lxml')
                    productCode = str(int(parse_qs(urlparse.urlparse(productUrl).query)['number'][0]))
                    productName = soup.find('h2')
                    if productName:
                        productName = productName.text
                    currPrice = soup.find('div', attrs={'class': 'lead', 'style': 'color:red'})
                    if currPrice:
                        currPrice = currPrice.find('span')
                        if currPrice:
                            currPrice = str(float(currPrice.text.replace(
                                'р. ', '.').replace('коп.', '')))
                        else:
                            currPrice = str(0)
                        oldPrice = soup.find('div', attrs={'class': 'lead'})
                        if oldPrice:
                            oldPrice = oldPrice.find('span')
                            if oldPrice:
                                oldPrice = str(float(oldPrice.text.replace('р. ', '.').replace('коп.', '')))
                            else:
                                oldPrice = str(0)
                    else:
                        currPrice = soup.find('div', attrs={'class': 'lead'})
                        if currPrice:
                            currPrice = currPrice.find('span')
                            if currPrice:
                                currPrice = str(float(currPrice.text.replace('р. ', '.').replace('коп.', '')))
                            else:
                                currPrice = str(0)
                        oldPrice = str(0)

                    sklad = soup.find('span', attrs={'class': 'sklad'})
                    if sklad is None:
                        sklad = 'Нет'
                    else:
                        sklad = 'Да'
                    
                    desc = soup.find('div', attrs={'class': 'desc'})
                    if desc:
                        desc = desc.text
                    divs = soup.find_all('table')[7].find_all('td')[1].find_all('div')
                    if soup.find('div', { 'class': 'vputi'}) is None:
                        add = 0
                    else:
                        add = 1
                    divsCount = len(divs)
                    params = divs[divsCount - 3 - add].find('strong')
                    if params:
                        params = 'Вес: ' + params.text
                    else:
                        params = ''
                    params2 = divs[divsCount - 2 - add].find('strong')
                    if params2:
                        params2 = 'Кол-во в упаковке: ' + params2.text
                    else:
                        params2 = ''
                    imgUrl = 'https://www.sat-altai.ru' + soup.find('img', {'class': 'img-polaroid'})['src']
                    array.append([
                        productCode,
                        category[1:],
                        productName,
                        currPrice,
                        oldPrice,
                        sklad,
                        desc,
                        params,
                        params2,
                        productUrl,
                        imgUrl,
                    ])

                except Exception:
                    print('-------------------------------------------Ошибка-------------------------------------------')
        category = category.replace('/' + li.find('a').text, '')

    return treeDict


def main():
    global array, cookies
    array = []
    cookies = {'beget': 'begetok'}
    response = requests.get(
        url='https://www.sat-altai.ru/catalog/?c=shop', cookies=cookies)
    soup = BeautifulSoup(response.text, 'lxml')

    tree = soup.find('div', {'id': 'tree'})
    tree = tree.find('ul')
    tree = perfomeTree(tree)

    df = pd.DataFrame(
        np.array(array)
    )
    df.columns = [
            'Артикул',
            'Категория',
            'Название',
            'Цена',
            'Старая цена',
            'Наличие товара',
            'Текстовое описание товара',
            'Параметры упаковки',
            'Комплектация товара',
            'Ссылка на товар',
            'Ссылка на картинку',
    ]
    df.to_csv('output.csv', index=False, sep=';')

if __name__ == '__main__':
    main()
