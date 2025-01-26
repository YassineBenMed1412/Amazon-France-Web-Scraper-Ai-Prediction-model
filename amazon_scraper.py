from datetime import datetime
import requests
import csv
import bs4

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 OPR/116.0.0.0"
REQUEST_HEADER = {
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US, en;q=0.5',
}


def get_page_html(url):
    try:
        res = requests.get(url=url, headers=REQUEST_HEADER, timeout=10)
        res.raise_for_status()
        return res.content
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


def get_product_price(soup):
    try:
        main_price_span = soup.find('span', attrs={
            'class': 'a-price aok-align-center'
        })
        if not main_price_span:
            return None
        price_spans = main_price_span.findAll('span')
        for span in price_spans:
            price = span.text.strip().replace('€', '').replace(',', '')
            try:
                return float(price)
            except ValueError:
                continue
        return None
    except Exception as e:
        print(f"Error parsing price: {e}")
        return None


def get_product_title(soup):
    try:
        product_title = soup.find('span', attrs={
            'id': 'productTitle'
        })
        return product_title.text.strip() if product_title else None
    except Exception as e:
        print(f"Error parsing title: {e}")
        return None
        
def get_product_rating(soup):
    try:
        product_rating = soup.find('span', attrs={
            'class': 'a-icon-alt'
    
        })
        ratings = product_rating.text.strip().split()
        return ratings[0] if product_rating else None
    except ValueError:
        print("Value Obtained For Rating Could Not Be Parsed")
        exit()
    
       
    
def extract_product_info(url):
    product_info = {'url': url}
    html = get_page_html(url=url)
    if not html:
        return None
    soup = bs4.BeautifulSoup(html, 'lxml')
    product_info['title'] = get_product_title(soup)
    product_info['price'] = get_product_price(soup)
    product_info['rating'] = get_product_rating(soup)
    return product_info


def main():
    products_data = []
    urls = []

    # Read URLs from CSV
    with open('amazon_products_urls.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        urls = [row[0] for row in reader]  # Flatten the list of rows

    # Sequentially scrape each URL
    for url in urls:
        print(f"Scraping: {url}")
        product_info = extract_product_info(url)
        if product_info:
            products_data.append(product_info)

    # Write the scraped data to a new CSV file
    output_file = 'scraped_products_data.csv'
    with open(output_file, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['title', 'price', 'rating','url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(products_data)

    print(f"Scraping completed. Data saved to {output_file}")


if __name__ == "__main__":
    main()