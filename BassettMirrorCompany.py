import re
import scrapy
import os
from scrapy.crawler import CrawlerProcess
import requests
from bs4 import BeautifulSoup
import csv
from playwright.sync_api import sync_playwright


def process_collection_products(page, collection_link, all_products):
    print(f"Processing  collection : {collection_link}")

    page.goto(collection_link)
    retry_count = 0
    max_retries = 3  

    while True:
        content = page.content()
        soup = BeautifulSoup(content, 'html.parser')
        products = soup.find_all("a", class_="col2 span_1_of_3 grid-tn")
        product_links = [
            "https://www.bassettmirror.com" + item.get('href').replace(" ", "%20")
            for item in products
        ]

        if len(product_links) > 0:
            print("Products found: ", len(product_links))

            for link in product_links:
                all_products.append(link)
            retry_count = 0
            next_page_locator = page.locator("#page-num a:has-text('>')")
            if next_page_locator.count() > 0:
                print("Navigating to the next page...")
                next_page_locator.click()
                page.wait_for_timeout(4000) 
            else:
                print("No more pages in this collection.")
                break
        else:
            if retry_count < max_retries:
                print(f"No products found. Retrying... ({retry_count + 1}/{max_retries})")
                page.reload()  
                page.wait_for_timeout(3000) 
                retry_count += 1
            else:
                print("Maximum retries reached. Skipping to the next collection.")
                break



def get_collections_products():
    output_file = 'utilities/products-links.csv'
    all_products = []  
    url = "https://www.bassettmirror.com/shop-products.cfm"
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html.parser")
    menu = soup.find("ul", id="menu")
    collections_link = menu.find_all("a")
    
    collections = []
    for item in collections_link:
        href = item.get("href")
        if href.startswith("/shop-products.") and not href.endswith("qs=1"):
            collections.append(
                "https://www.bassettmirror.com" + href.replace(" ", "%20")
            )

    if collections:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            for collection in collections:
                process_collection_products(
                    page, 
                    collection, 
                    all_products
                )

            browser.close()

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['product_link']) 
        for product_link in all_products:
            writer.writerow([product_link]) 

    print("Scraping completed and data saved to CSV.")


# --------------------------------------------------------------------------------------------------------------------------------------------

class ProductSpider(scrapy.Spider):
    name = "product_spider"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1,
        'LOG_LEVEL': 'INFO',
        'RETRY_ENABLED': True,
        'RETRY_TIMES': 3,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429],
        'HTTPERROR_ALLOW_ALL': True,
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                          'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                          'Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'en',
        },
    }

    columns = [
        "SKU", "START_DATE", "END_DATE", "DATE_QUALIFIER", "DISCONTINUED", "BRAND", "PRODUCT_GROUP1",
        "PRODUCT_GROUP2", "PRODUCT_GROUP3", "PRODUCT_GROUP4", "PRODUCT_GROUP1_QTY", "PRODUCT_GROUP2_QTY",
        "PRODUCT_GROUP3_QTY", "PRODUCT_GROUP4_QTY", "DEPARTMENT1", "ROOM1", "ROOM2", "ROOM3", "ROOM4",
        "ROOM5", "ROOM6", "CATEGORY1", "CATEGORY2", "CATEGORY3", "CATEGORY4", "CATEGORY5", "CATEGORY6",
        "COLLECTION", "FINISH1", "FINISH2", "FINISH3", "MATERIAL", "MOTION_TYPE1", "MOTION_TYPE2",
        "SECTIONAL", "TYPE1", "SUBTYPE1A", "SUBTYPE1B", "TYPE2", "SUBTYPE2A", "SUBTYPE2B",
        "TYPE3", "SUBTYPE3A", "SUBTYPE3B", "STYLE", "SUITE", "COUNTRY_OF_ORIGIN", "MADE_IN_USA",
        "BED_SIZE1", "FEATURES1", "TABLE_TYPE", "SEAT_TYPE", "WIDTH", "DEPTH", "HEIGHT", "LENGTH",
        "INSIDE_WIDTH", "INSIDE_DEPTH", "INSIDE_HEIGHT", "WEIGHT", "VOLUME", "DIAMETER", "ARM_HEIGHT",
        "SEAT_DEPTH", "SEAT_HEIGHT", "SEAT_WIDTH", "HEADBOARD_HEIGHT", "FOOTBOARD_HEIGHT",
        "NUMBER_OF_DRAWERS", "NUMBER_OF_LEAVES", "NUMBER_OF_SHELVES", "CARTON_WIDTH", "CARTON_DEPTH",
        "CARTON_HEIGHT", "CARTON_WEIGHT", "CARTON_VOLUME", "CARTON_LENGTH", "PHOTO1", "PHOTO2",
        "PHOTO3", "PHOTO4", "PHOTO5", "PHOTO6", "PHOTO7", "PHOTO8", "PHOTO9", "PHOTO10", "INFO1",
        "INFO2", "INFO3", "INFO4", "INFO5", "DESCRIPTION", "PRODUCT_DESCRIPTION",
        "SPECIFICATIONS", "CONSTRUCTION", "COLLECTION_FEATURES", "WARRANTY", "ADDITIONAL_INFORMATION",
        "DISCLAIMER", "VIEWTYPE", "ITEM_URL", "CATALOG_PDF",
    ]

    def __init__(self, input_file='utilities/products-links.csv', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.input_file = input_file
        os.makedirs('output', exist_ok=True)
        self.bassett_mirror_company_file = open('output/bassett_mirror_companye.csv', 'w', newline='', encoding='utf-8')

        self.bassett_mirror_company_writer = csv.DictWriter(self.bassett_mirror_company_file, fieldnames=self.columns)

        self.bassett_mirror_company_writer.writeheader()


    def start_requests(self):
        self.logger.info("Spider started. Reading product links from CSV file.")
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                yield scrapy.Request(
                    url=row['product_link'],
                    callback=self.parse,
                    meta={
                        'product_link': row['product_link']
                    }
                )
    def parse(self, response):
        self.logger.info(f"Parsing product: {response.url}")
        sku = ""
        product_title = ""
        width = ""
        depth = ""
        height = ""
        description = ""
        material = ""
        finish = ""
        category1 = ""
        category2 = ""
        category3 = ""
        collection = ''
        products_images = []
        product_description = ""
        specifications = ""
        specifications_str = ""
        catalog_pdf = ""
        try:
            meta = response.meta
            soup = BeautifulSoup(response.text, 'html.parser')

            data = {col: "" for col in self.columns} 


            try:
                spec = soup.find('div', class_="spec").get_text().strip()
                clean_spec = spec.replace('\xa0', ' ')
                if "|" in clean_spec:
                    sku, dim = clean_spec.split("|")
                    sku = sku.strip()
                    dim = dim.strip()
                    dims = dim.split("x")
                    if len(dims)==3:
                        width, depth, height = dims
                    elif len(dims)==2:
                        width, height = dims
                else:
                    sku = clean_spec
                    width, depth, height = ""
 
            except Exception as e:
                print("An error occurred while extracting SKU:", str(e))


            try:
                product_title = soup.find("span", class_ = "pageTitle")
                if product_title:
                    product_title = product_title.text.strip()
            except AttributeError:
                product_title = ""

            try:
                description_container = soup.find("div", class_="col span_1_of_3")
                if description_container:
                    description_paragraph = description_container.find("p")
                    if description_paragraph:
                        product_description = description_paragraph.get_text(strip=True)
            except AttributeError:
                product_description = ""

            try:
                specifiation_div = soup.find("div", class_ = "panel" )
                specifications = {}
                if specifiation_div:
                    items = specifiation_div.find_all('li')
                    if items:
                        for item in items:
                            key, value = item.get_text().split(":", 1)
                            specifications[key] = value

                if specifications:
                    style = specifications.get("Style", None)
                    material = specifications.get("Material", None)
                    finish = specifications.get("Color/Finish", None)
                specifications_str = "; ".join([f"{k}: {v}" for k, v in specifications.items()])
            except AttributeError:
                specifications_str = ""

            paths_div = soup.find("div", class_ = "master-width breadcrumbs")
            if paths_div:
                paths_span = paths_div.find("span", class_ = "breadcrumbs")
                if paths_span:
                    paths = paths_span.get_text(strip = True).split("/")

                    if len(paths) ==4:
                        category1 = paths[0]
                        category2 = paths[1]
                        category3 = paths[2]
                        collection = paths[3]
                    elif len(paths)==3:
                        category1 = paths[0]
                        category2 = paths[1]
                        collection = paths[2]

            try:
                description_div = soup.find('div', class_ = 'spec spec_desc')
                description = []
                if description_div:
                    description_items = description_div.find_all("td")
                    if description_items:
                        for item in description_items:
                            description.append(item.get_text(strip = True))
            except AttributeError:
                description = ""
               
            try:
                catalog_pdf = soup.find('a', class_ = "btn-tearsheet")
                if catalog_pdf:
                    catalog_pdf = catalog_pdf.get("href")
            except:
                catalog_pdf = ""

            data.update({
                "CATEGORY1": category1,
                "CATEGORY2": category2,
                "CATEGORY3": category3,
                "COLLECTION": collection,
                "ITEM_URL": meta['product_link'],
                "SKU": sku,
                "DESCRIPTION": ", ".join(description) if isinstance(description, list) else description,
                "PRODUCT_DESCRIPTION": product_description,
                "WIDTH": width,
                "DEPTH": depth,
                "HEIGHT": height,
                "STYLE": style,
                "ADDITIONAL_INFORMATION": material,
                "FINISH1": finish,
                "CONSTRUCTION": "", 
                "SPECIFICATIONS": specifications_str,
                "BRAND": "Bassett Mirror",
                "VIEWTYPE": "Normal",  
                "CATALOG_PDF" : catalog_pdf, 
            })

            try:
                image_urls = []
                gallery_div = soup.find("div", id="gallery")
                if gallery_div:
                    image_divs = gallery_div.find_all("div", class_="tn")
                    for div in image_divs:
                        st = div.get("style")
                        if st:
                            url_match = re.search(r'background-image:url\((.*?)\);', st)
                            if url_match:
                                image_urls.append(url_match.group(1))
                                products_images = image_urls
            except AttributeError:
                products_images = []

            if len(products_images) == 0:
                img_url = soup.find("div", id = "main-image")
                if img_url:
                    img_url = img_url.get("style")
                    img_url = re.search(r'background-image:url\((.*?)\);', img_url)
                    img_url = img_url.group(1)
                    products_images.append(img_url)
                
            for i in range(1, 11):
                data[f"PHOTO{i}"] = ""
            for idx, img_url in enumerate(products_images):
                if idx > 9:
                    continue
                else:
                    data[f"PHOTO{idx + 1}"] = str(img_url).replace("'", "")
            if len(products_images) < 10:
                self.logger.info(f"Only {len(products_images)} images found for {meta['product_link']}. Remaining PHOTO columns will be ''.")
            elif len(products_images) > 10:
                self.logger.warning(f"More than 10 images found for {meta['product_link']}. Only the first 10 will be saved.")

            if len(products_images) == 0:
                data.update({
                    "VIEWTYPE": "Limited",
                })

            if sku:
                self.bassett_mirror_company_writer.writerow(data)
                self.logger.info(f"Successfully scraped and categorized product: {meta['product_link']}")
            else:
                self.logger.info("############################ Missing SKU Detected  ###########################################")
                self.logger.info(soup.find('div', class_="spec").get_text().strip())
                self.logger.info("Product link : ", meta['product_link'])
                self.logger.info("############################ Missing SKU Detected  ###########################################")
        except Exception as e:
            self.logger.error(f"Error parsing product: {response.url}, {e}")

    def closed(self, reason):
        self.bassett_mirror_company_file.close()
        self.logger.info("Spider closed. Files saved.")
 


# ----------------------------------------    RUN THE CODE   --------------------------------------------------------------------------------------------------
if __name__ == "__main__":

    # output_dir = 'utilities'
    # os.makedirs(output_dir, exist_ok=True)
    # get_collections_products()
    process = CrawlerProcess()
    process.crawl(ProductSpider)
    process.start()
