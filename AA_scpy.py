import requests
from bs4 import BeautifulSoup
import json
import time

def extract_product_data(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        return None
        
    soup = BeautifulSoup(res.text, 'html.parser')
    
    data = {
        "Productname": "",
        "Brand": "",
        "Reviews": "",
        "Availability": "",
        "Price": "",
        "Features": "",
        "specifications": ""
    }
    
    title_tag = soup.find('h1')
    if title_tag:
        data["Productname"] = title_tag.get_text(strip=True)
        
    price_tag = soup.select_one('.price-new') or soup.select_one('.price h2') or soup.select_one('ul.list-unstyled h2')
    if price_tag:
        data["Price"] = price_tag.get_text(strip=True)
        
    list_items = soup.select('ul.list-unstyled li')
    for li in list_items:
        text = li.get_text(strip=True)
        if text.startswith('Brand:'):
            data["Brand"] = text.replace('Brand:', '').strip()
        elif text.startswith('Availability:'):
            data["Availability"] = text.replace('Availability:', '').strip()
            
    review_tag = soup.find('a', href="#tab-review")
    if review_tag:
        data["Reviews"] = review_tag.get_text(strip=True)
        
    desc_tab = soup.find('div', id='tab-description')
    if desc_tab:
        data["Features"] = desc_tab.get_text(separator=' ', strip=True)
        
    spec_tab = soup.find('div', id='tab-specification')
    if spec_tab:
        spec_dict = {}
        rows = spec_tab.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 2:
                key = cols[0].get_text(strip=True)
                val = cols[1].get_text(strip=True)
                spec_dict[key] = val
        data["specifications"] = spec_dict
        
    return data

def main():
    base_url = "https://mdcomputers.in/?route=product/search&search=external%20harddrive&page="
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    }
    
    results = []
    
    for page in range(1, 4):
        search_url = base_url + str(page)
        res = requests.get(search_url, headers=headers)
        if res.status_code != 200:
            continue
            
        soup = BeautifulSoup(res.text, 'html.parser')
        
        product_links = []
        for item in soup.select('.product-layout .caption h4 a'):
            link = item.get('href')
            if link:
                product_links.append(link)
                
        for link in product_links:
            product_data = extract_product_data(link)
            if product_data:
                results.append(product_data)
            time.sleep(1)
            
    with open('harddrives_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
