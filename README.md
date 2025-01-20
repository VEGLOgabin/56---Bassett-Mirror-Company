# 56---Bassett-Mirror-Company
<div class="prod-img" id="main-image" style="background-image:url('https://files.plytix.com/api/v1.1/file/public_files/pim/assets/99/e7/bd/62/62bde79981697600089987d9/images/e9/3c/7d/67/677d3ce9629679a9c64e6f7c/2485-700-906.jpg?s=1000x'); ">
				
				<a class="productPhoto" href="#enlarge"><img src="/images/expand.svg" border="0" class="icon"></a>		
			</div>

here is the differents columns:

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
        "DISCLAIMER", "VIEWTYPE", "ITEM_URL"
    ]


so i need the specification inside the specification column and also get so columns data  from it and assign them to their respective column



others data presents:

additional_info_div = soup.find('div', class_ = 'spec spec_desc')
additional_info = []
if additional_info_div:
    additional_info_items = additional_info_div.find_all("td")
    if additional_info_items:
        for item in additional_info_items:
            additional_info.append(item.get_text(strip = True))



# Scraping image URLs from the gallery
image_urls = []
gallery_div = soup.find("div", id="gallery")
if gallery_div:
    image_divs = gallery_div.find_all("div", class_="tn")
    for div in image_divs:
        style = div.get("style")
        if style:
            # Extract the URL from the background-image style
            url_match = re.search(r'background-image:url\((.*?)\);', style)
            if url_match:
                image_urls.append(url_match.group(1))

product_images = image_urls



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


product_title = soup.find("span", class_ = "pageTitle").text.strip()

spec = soup.find('div', class_="spec").get_text().strip()
clean_spec = spec.replace('\xa0', ' ')

sku, dim = clean_spec.split("|")

sku = sku.strip()
dim = dim.strip()

dims = dim.split("x")

if len(dims)==3:
    width, depth, height = dims
elif len(dims)==2:
    width, height = dims