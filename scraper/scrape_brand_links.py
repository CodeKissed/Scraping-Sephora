import requests
from bs4 import BeautifulSoup

# Get Response of "brandlist" Website from Sephora
band_lst_link = "https://www.sephora.com/ca/en/brands-list"
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:137.0) Gecko/20100101 Firefox/137.0'})
response = session.get(band_lst_link)

# Use BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Scraping brand links and save them into a list
brand_link_lst = []
for brand in soup.find_all(attrs={'data-at': 'brand_link'}):
    brand_link_lst.append("https://www.sephora.com" +
                          brand.attrs['href']+"/all?pageSize=300")

# Write brand links into a file:
with open('data/brand_link.txt', 'w') as f:
    for item in brand_link_lst:
        f.write(f"{item}\n")

# Indicate scraping completion
print(f'Got All Brand Links! There are {len(brand_link_lst)} brands in total.')
