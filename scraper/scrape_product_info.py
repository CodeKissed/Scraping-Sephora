import json
import sys
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup


def new_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0'})
    return s


session = new_session()


def get_data(product_link, px_list=None):
    """Get product information"""
    data_dic = {'pd_id': [], 'size_and_item': [], 'category': [],
                'price': [], 'love_count': [], 'reviews_count': []}
    px_idx = 0
    proxy = None if px_list is None else px_list[px_idx]

    while True:
        try:
            response = session.get(product_link, proxies={
                "http": proxy, "https": proxy}, timeout=15)
        except:
            if px_idx == len(px_list) - 1:
                px_idx = 0
            else:
                px_idx += 1
            proxy = px_list[px_idx]
            continue

        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        jsonld = {
            data['@type']: data
            for data in [
                json.loads(jsondata.string)
                for jsondata in soup.find_all(
                    'script', attrs={'type': 'application/ld+json'})]
        }

        linkstore = json.loads(
            soup.find('script', id='linkStore',
                      attrs={'type': 'text/json', 'data-comp': 'PageJSON '}).string
        )

        data_dic['pd_id'] = linkstore['page']['product']['productId']
        data_dic['product_name'] = linkstore['page']['product']['currentSku']['productName']

        data_dic['category'] = ', '.join(
            [item['item']['name']
             for item in jsonld['BreadcrumbList']['itemListElement']])

        try:
            data_dic['size_and_item'] = linkstore['page']['product']['currentSku']['size']
        except KeyError:
            data_dic['size_and_item']=None

        data_dic['price'] = linkstore['page']['product']['currentSku']['listPrice'].replace('$', '')
        data_dic['rating'] = linkstore['page']['product']['productDetails']['rating']
        data_dic['reviews_count'] = linkstore['page']['product']['productDetails']['reviews']
        data_dic['love_count'] = linkstore['page']['product']['productDetails']['lovesCount']
        data_dic['brand_id'] = linkstore['page']['product']['productDetails']['brand']['brandId']
        data_dic['brand_name'] = linkstore['page']['product']['productDetails']['brand']['displayName']
        data_dic['ingredients'] = linkstore['page']['product']['currentSku']['ingredientDesc']
        data_dic['limited_edition'] = linkstore['page']['product']['currentSku']['isLimitedEdition']
        data_dic['new'] = linkstore['page']['product']['currentSku']['isNew']
        data_dic['exclusive'] = linkstore['page']['product']['currentSku']['isSephoraExclusive']
        data_dic['online_only'] = linkstore['page']['product']['currentSku']['isOnlineOnly']
        data_dic['highlights'] = ', '.join([
            hl['name']
            for hl in linkstore['page']['product']['currentSku']['highlights']
        ])

        break
    return data_dic


# px_list_ = ['140.227.173.230:1000', '140.227.224.177:1000',
#             '140.227.225.38:1000', '140.227.237.154:1000',
#             '40.227.174.216:1000', '140.227.175.225:1000',
#             '140.227.229.208:3128', '155.138.135.199:8080',
#             '149.28.54.243:8080', '64.188.3.162:3128',
#             '165.22.211.212:3128']
px_list_ = [None]

pd_links_df = pd.read_csv('data/product_links.csv')
product_links = pd_links_df['product_links']
result = []

for i, link in enumerate(product_links[:]):
    try:
        data = get_data(link, px_list_)
        result.append(data)
    except KeyError:
        print(f"!!! skipping {link}", file=sys.stderr)
        pass
    pd_df = pd.DataFrame(result)
    pd_df.to_csv('data/pd_info.csv', index=False)
    print(f'{i + 1:04d} / {len(product_links)} || {link}')
    time.sleep(0.2)
