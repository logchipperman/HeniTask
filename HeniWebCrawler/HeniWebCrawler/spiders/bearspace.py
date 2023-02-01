import re
from scrapy.spiders import SitemapSpider

class BearspaceSpider(SitemapSpider):
    """Spider for https://www.bearspace.co.uk
    Crawls paintings from https://www.bearspace.co.uk/purchase
    Using the sitemap.

    Could also of been done by getting the urls from https://www.bearspace.co.uk/purchase
    by parsing the json data in script#wix-warmup-data

    Or you could paginate by incrementing the page number but that would require
    making more requests.
    """
    
    name = 'bearspace'
    allowed_domains = ['bearspace.co.uk']
    sitemap_urls = ('https://www.bearspace.co.uk/store-products-sitemap.xml',)
    sitemap_rules = [(r"/product-page/", "parse")]

    dimensions_regex = (r"(?P<height>\d+[,\.]?\d*)\s{0,4}(?:by|x|×)?\s{0,4}"
                        r"(?P<width>\d+[,\.]?\d*)\s{0,4}(?:by|x|×)?\s{0,4}"
                        r"(?P<depth>\d+[,\.]?\d*)?\s{0,4}(?P<unit>cm)")

    def parse(self, response):
        paintingItem = {}
        
        paintingItem["url"] = response.url

        # These could all be xpaths if needed, depends on the preference of the reviewer. 
        title = response.css("h1[data-hook='product-title']::text").get()
        paintingItem["title"] = title

        media = response.css("pre[data-hook='description'] > p:nth-of-type(1) *::text").get()
        paintingItem["media"] = media

        description_strings = response.css("pre[data-hook='description'] p *::text").getall()
        for description_string in description_strings:
            if dimensions_re := re.search(self.dimensions_regex, description_string, re.IGNORECASE):
                paintingItem["height_cm"] = dimensions_re.group("height")
                paintingItem["width_cm"] = dimensions_re.group("width")

        price_gbp = response.css("span[data-hook='formatted-primary-price'] *::text").re_first(r"£(.*)")
        paintingItem["price_gbp"] = price_gbp

        yield paintingItem
