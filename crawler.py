import scrapy
from scrapy.crawler import CrawlerProcess
import json
from itemadapter import ItemAdapter
from bs4 import BeautifulSoup

from scrapy.item import Item, Field

class BlogSpider(scrapy.Spider):
    name = 'blogspider'
    start_urls = ['https://go.kompas.com/read/2022/05/24/160545274/who-chief-the-pandemic-is-most-certainly-not-over']

    def parse(self, response):
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        yield {
            'judul': extract_with_css('h1.read__title::text'),
            'konten': response.css('div.read__content p::text').getall(),
        }

        next_page = response.css('div.col-bs12-2 a::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

process = CrawlerProcess(settings={
    "FEEDS": {
        "items.json": {
            "format": "json",
            }
    },
})

# This is used to call crawler directly from running. 
process.crawl(BlogSpider)
process.start()
# otherwise, just use: scrapy runspider main.py in terminal


# Opening JSON file
f = open('items.json')
  
# returns JSON object as a dictionary
data = json.load(f)
  
# Iterating through the json list
for berita in data:
    berita["konten"] = (''.join(berita["konten"]))
    print(berita["konten"])

print(data)

# Modifying Json
edit = open("items.json", "w")
json.dump(data, edit)
edit.close()

# Closing file
f.close()

