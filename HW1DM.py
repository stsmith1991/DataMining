#Б#Библиотеки
from pathlib import Path
import time
import json
import requests
#Методы парсинга
class Parse5ka:

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0"
        }

    def __init__(self, main_url: str, cags_path: str, products_path: str,  save_path: Path):
        self.main_url = main_url
        self.cags_path = cags_path
        self.products_path = products_path
        self.save_path = save_path

    def get_response_from(self, url, **params) -> requests.Response:
        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code in (200, 301, 304):
                return response
            time.sleep(0.2)

    def run(self):
        for category_id, category_name in self.parse_category(self.main_url + self.cags_path + '/'):
            category_path = self.save_path.joinpath(f"{category_id}_{category_name}.json")
            for product in self.parse_products(self.main_url + self.products_path + '/', category_id):
                self.save_to_file(category_path, product)
            else:
                category_path.touch()

    def parse_category(self, url):
        categories_response = self.get_response_from(url)
        for parent_category in categories_response.json():
            parent_category_url = url + parent_category.get('parent_group_code') + '/'
            parent_response = self.get_response_from(parent_category_url)
            if parent_response.content is []:
                yield int(parent_category.get('parent_group_code')), parent_category.get('parent_group_name')
            else:
                for category in parent_response.json():
                    yield int(category.get('group_code')), category.get('group_name')

    def parse_products(self, url, cat_id):
        ismay = False
        while url:
            if not ismay:
                response = self.get_response_from(url, categories=cat_id)
            else:
                response = self.get_response_from(url)
            data: dict = response.json()
            url = data.get("next")
            for product in data.get("results", []):
                yield product
            ismay = True

    def save_to_file(self, file_path, data):
        with open(file_path, mode='a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name):
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path


if __name__ == "__main__":
    parser = Parse5ka(main_url="https://5ka.ru/api/v2/",
                      cags_path='categories',
                      products_path='special_offers',
                      save_path=get_save_path("categories")
                      )

#Главкод
parser.run()