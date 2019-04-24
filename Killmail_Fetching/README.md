# eve-trajectory-mining #

-----

## Killmail Fetching Application

The scripts and modules in this section are dedicated to acquiring Killmail
data from http://www.zkillboard.com/ (ZKB), for later use in the Trajectory 
Mining Application.

## Motivation/Parameters:

Algorithm:

1. Call one page of one month of killmail data in a given year and region

2. While parsing this page, the next page request will be put on hold. This is
   because price information for all item ids that are scraped from the
   victims in each killmail on the page are looked up, as follows:

  1. The price of an item_id on a specific killmail's date is stored by
     item_id and killmail_date in a client-side chained hash table. Thus, the
     client will first ask if the price exists already for a specific item, on
     a specific date and use the stored value, if it exists.  

  2. If the price is not found by item_id or date (either one or both may be
     missing) in the chained hash table, a lookup table is established for the
     entire killmail page, and every time a new item_id and/or date is
     encountered, it is stored to the look-up table as item_id -> date ->
     (location_in_killmail, quantity)  

  3. Once the killmail page has finished parsing, and all item_id -> date
     combos have either been found in the client-side hash table or added to
     the look-up table, the look-up table is then traversed, and for every
     item_id, a request is sent to the corresponding price page. The API is
     scraped, and for each date that was hashed under the item_id key, the
     corresponding price is found on the page. In this way, a price page does
     not get visited more than once per killmail page!  

  4. The price information is stored in the client-side table, then added to
     the data scraped from the killmail page

3. Once all prices have been looked-up and acquired, a new page request will
   be generated for the next page in the given month/year/regionID path. Once
   all pages are exhausted and an empty list is returned from a page, the next
   month/year/regionID combination is computed, and this algorithm repeats
   until all month/year/regionID/page paths have been requested, and all price
   information gathered!  

## Tech/Framework used:

**Built with**
- `Python 3.6`
- `Scrapy 1.5.0`
- `Twisted 13.1.0`

## Features:

- Able to concurrently run parallel processes for scraping many different
  sections of the ZKB API, reducing time of acquisition by allowing for rapid
  request generation and link following across one large process, albeit at
  the cost of resource consumption.

- Able to sequentially queue concurrent parallel processes, to allow for
  breakpoints in scraping, thus producing small sections of data sooner and
  allowing for more control during the scraping process, albeit at a slower
  pace overall.

## Installation:

In order to use/modify the scripts here, `Python 3.6` must be installed on your
system. Go to http://python.org/ to learn more.

If `PyPI` is installed, then simply run `$pip install Scrapy` in this machine's
local Terminal (MAC and Linux) or Commmand Prompt (Windows) to install
**Scrapy** and its dependencies.
  - **Always** check https://doc.scrapy.org/en/latest/intro/install.html for
    the latest installation guide.

## API Reference:

Much of this application is implemented in a **Scrapy** framework, built on top
of a **Twisted** reactor. To get started, follow the **Scrapy** tutorial at https://doc.scrapy.org/en/latest/intro/tutorial.html

After following the tutorial, it will help to become familiar with each
libraries' documentation, found at https://doc.scrapy.org/en/latest/index.html.
Particularly useful pages:

- **Scrapy** `Spiders` |> See
  https://doc.scrapy.org/en/latest/topics/spiders.html
- **Scrapy** `API` |> See
  https://doc.scrapy.org/en/latest/topics/api.html
- **Scrapy** `Settings` |> See
  https://doc.scrapy.org/en/latest/topics/settings.html
- **Scrapy** Architecture |> See
  https://doc.scrapy.org/en/latest/topics/architecture.html
- Common Practices (For running **Scrapy** from a script) |> See
  https://doc.scrapy.org/en/latest/topics/practices.html

## How to Get Started Using This Application?

To begin any custom scrape job, simply run either **CrawlSeqRegionsPP.py** or
**CrawlConcPP.py** in a **Python** shell, or from your favorite
Terminal-based program!

When ready to implement a custom scrape job, then for all parts of this
application, follow the instructions in the comments and
function/method documentation in order to modify the behavior of the
application.

***IMPORTANT:*** ALWAYS READ THE DOCUMENTATION AT THE TOP OF EACH FILE FIRST!

To get started on which file to modify, follow this handy guide!

If you need to...
- Create a custom scraping range
- Control the queuing of spiders
- Modify the starting URLS of each spider  

Then modify either **CrawlSeqRegionsPP.py** or **CrawlConcPP.py**,
depending on your scraping needs.

If you need to...
- Modify how data is parsed from ***ZKillboard***
- Modify the logic used to create new links to follow from the starting URL
- Change the rules for handling website responses

Then modify **/Killmail_Fetching/spiders/zkbspider.py**!

If you need to...
- Filter scraped data after the spider acquires it
- Change how the scraped data is processed/stored

Then modify **/Killmail_Fetching/pipelines.py**!

## Credits:

Designed and Developed exclusively by Adam Coscia.

Created: 06/25/2018
