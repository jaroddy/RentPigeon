"""
This example run script shows how to run the Zillow scraper defined in ./zillow.py
It scrapes hotel data and saves it to ./results/

To run this script set the env variable $SCRAPFLY_KEY with your scrapfly API key:
$ export $SCRAPFLY_KEY="your key from https://scrapfly.io/dashboard"
"""
import asyncio
import json
from pathlib import Path
import zillow

output = Path(__file__).parent / "results"
output.mkdir(exist_ok=True)


async def run():
    # enable scrapfly cache for basic use
    zillow.BASE_CONFIG["cache"] = True

    print("running Zillow scrape and saving results to ./results directory")

    url = "https://www.zillow.com/homes/for_rent/house,townhouse_type/?searchQueryState=%7B%22isMapVisible%22%3Atrue%2C%22mapBounds%22%3A%7B%22west%22%3A-122.60589514318848%2C%22east%22%3A-121.99924383703613%2C%22south%22%3A47.528815013476816%2C%22north%22%3A47.799110548263194%7D%2C%22filterState%22%3A%7B%22price%22%3A%7B%22min%22%3Anull%2C%22max%22%3A392948%7D%2C%22mf%22%3A%7B%22value%22%3Afalse%7D%2C%22con%22%3A%7B%22value%22%3Afalse%7D%2C%22land%22%3A%7B%22value%22%3Afalse%7D%2C%22apa%22%3A%7B%22value%22%3Afalse%7D%2C%22manu%22%3A%7B%22value%22%3Afalse%7D%2C%22apco%22%3A%7B%22value%22%3Afalse%7D%2C%22mp%22%3A%7B%22max%22%3A2000%7D%2C%22fsba%22%3A%7B%22value%22%3Afalse%7D%2C%22fsbo%22%3A%7B%22value%22%3Afalse%7D%2C%22nc%22%3A%7B%22value%22%3Afalse%7D%2C%22cmsn%22%3A%7B%22value%22%3Afalse%7D%2C%22auc%22%3A%7B%22value%22%3Afalse%7D%2C%22fore%22%3A%7B%22value%22%3Afalse%7D%2C%22fr%22%3A%7B%22value%22%3Atrue%7D%7D%2C%22isListVisible%22%3Atrue%2C%22mapZoom%22%3A12%2C%22pagination%22%3A%7B%7D%2C%22usersSearchTerm%22%3A%22%22%7D"
    result_location = await zillow.scrape_search(url=url, max_scrape_pages=3)
    output.joinpath("search.json").write_text(json.dumps(result_location, indent=2, ensure_ascii=False))

    url = "https://www.zillow.com/homedetails/661-Lakeview-Ave-San-Francisco-CA-94112/15192198_zpid/"
    #result_property = await zillow.scrape_properties([url,])
    #output.joinpath("property.json").write_text(json.dumps(result_property[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(run())
