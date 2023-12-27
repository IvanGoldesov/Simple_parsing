import requests
import csv
import re
from bs4 import BeautifulSoup
from model import Product


def parser(url : str):
    #Доступные вкладки на рассматриваемом сайте
    categories = ['kicks', 'clothes', 'accessories', 'figurines', 'sareproducts', 'baby']

    for category in categories:
        create_csv(category)
        counter = 1

        res = requests.get(f'{url}{category}/page/{counter}/')
        soup = BeautifulSoup(res.text, 'lxml')
        list_product = []
        
        error = soup.find('h1', class_ = 'page-title')

        while not error:
            print(counter)
            #Получаем доступ ко всем кроссовкам
            catalog_items = soup.find_all('article', class_ = 'catalog__item')

            #перебираем кроссовки
            for item in catalog_items:
                
                pricee = []
                #Получаем ссылку на каждый товар отдельно
                link = item.find('a', class_ = 'catalog__img-link').get('href')
                #Выполняем запрос и переход на страницу каждого товара
                res_link = requests.get(url = link)
                soup_link = BeautifulSoup(res_link.text, 'lxml')

                #Получаем цену товара
                prices = item.find_all('bdi')

                #Если цена лежит в дапазоне или действует скидка
                if len(prices) > 1:
                    for price in range(len(prices)):
                        pricee.append(''.join(re.findall('\d', (prices[price].get_text()))))

                #Если цена на товары одна
                elif len(prices) == 1:
                    pricee.append(''.join(re.findall('\d', (prices[0].get_text()))))

                else:
                    pricee.append('None')
                    
                
                #Получаем код сведения о товаре для дальнейшего парсинга
                things = soup_link.find_all('div', class_ = 'product__wrap clearfix')

                #Разбираем каждый товар отдельно
                for thing in things:
                    
                    sizes = []

                    #Получаем название товара
                    name = thing.find('h1', class_ = 'product_title entry-title').string
                    
                    
                    #Получаем фото товара
                    img = thing.find('a', class_ = 'active').find('img').get('src')

                    #Получаем доступные размеры товара
                    size = thing.find('select', attrs={'name':'attribute_pa_eu'})
                    if size:
                        size = size.find_all()
                        for s in range(1, len(size)):
                            sizes.append(size[s].get_text())
                    else:
                        sizes.append('None')

                #Добавляем новые товары в список
                if len(pricee) > 1:
                    list_product.append(Product(link=link, name=name, SALE=('YES' if int(pricee[0]) > int(pricee[1]) else 'NO'), 
                                                price=' - '.join(pricee), img=img, available_sizes=', '.join(sizes)))
                else:
                    list_product.append(Product(link=link, name=name, SALE='NO', price=pricee[0], 
                                                img=img, available_sizes=', '.join(sizes)))
                    
            #Для обновления страничек
            counter += 1

            #Делаем запрос новой страницы
            res = requests.get(f'{url}{category}/page/{counter}/')
            soup = BeautifulSoup(res.text, 'lxml')

            #Если такой страницы не существует (она последняя, то строку с напоминанием об этом)
            error = soup.find('h1', class_ = 'page-title')

        write_csv(list_product, category)

#Создаём новый csv файл в котором будем хранить запрошенные данные
def create_csv(name_file : str):
    with open(f'Informations\{name_file}.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'name',
            'SALE',
            'price(Rub)',
            'available_sizes(EU)',
            'img',
            'link'
        ])

#Добавляем новые данные в файл
def write_csv(products : list[Product], name_file : str):
    with open(f'Informations\{name_file}.csv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for product in products:
            writer.writerow([
                product.name,
                product.SALE,
                product.price,
                product.available_sizes,
                product.img,
                product.link
            ])


#Запуск основной части программы
if __name__ == '__main__':
    parser(url = 'https://kicksmania.ru/shop/categories-')