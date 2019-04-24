# -*- coding: utf-8 -*-
"""ZKillBoard Killmail and Item Price Extraction Script (Concurrently)

====================IMPORTANT====================READ BELOW====================

IF USING MAC:
    Must run `$ulimit -Sn 10,000`!! Must allow MANY open files at the
    same time or the system will crash horribly :(

CHECK SETTINGS.PY!!!
This is where project wide settings are enabled. Currently enabled settings:
    ROBOTSTXT_OBEY = True
    COOKIES_ENABLED = False
    AUTOTHROTTLE_ENABLED = True
    ^^See https://doc.scrapy.org/en/latest/topics/autothrottle.html
    LOG_LEVEL = 'INFO'
    ^^See https://doc.scrapy.org/en/latest/topics/settings.html#log-level

====================IMPORTANT====================READ ABOVE====================

This script scrapes all pages of a given month/year/regionID URL path. Thus, 148
spiders will each crawl a unique month and regionID from 05-2015 to 05-2018
concurrently, until all pages have been crawled.

Extraction API:
    https://github.com/zKillboard/zKillboard/wiki/API-(Killmails)

Created by: Adam Coscia
Created on: 07-10-2018
Last Modified: 07-17-2018
"""
import logging

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from Killmail_Fetching.spiders.zkbspider import ZKBSpider


class ZKBPage(object):
    """Creates and updates path modifiers used in requests made by spiders.

    URLS for each spider are relative to 4 sets of path element:identifier
    strings: `RegionID` : ``str`` | `year` : ``str`` | `month` : ``str`` |
    `page` : ``str``

    Every time `self.update_path_modifiers` is called, `self.path_elem` is
    updated with the next month and/or year sequentially from the previous
    month/year. If end date is reached, date is set back to the starting
    date, the month and year lists are reset, and a new regionID is used. The
    process repeats until no month/year/RegionID combinations exist, at which
    point `self.path_elem` is set to None.

    """

    def __init__(self):
        # Lists of path element strings to populate new URLs string with
        self.months = ['06', '07', '08', '09', '10', '11', '12', '01', '02',
                       '03', '04']
        self.months_itr = iter(self.months)
        self.years = ['2016', '2017', '2018']
        self.years_itr = iter(self.years)
        self.regions = ['10000016', '10000033', '10000069']
        self.regions_itr = iter(self.regions)

        # Starting path elements: Page 1 of Region 10000002 on 05/2015
        self.path_elem = [
            'https:', '', 'zkillboard.com', 'api', 'kills', 'regionID',
            '10000002', 'year', '2015', 'month', '05', 'page', '1', ''
        ]

    def update_path_modifiers(self):
        """Updates instance path elements until end date is reached.

        Important fields:
            page: self.path_elem[-2]  month: self.path_elem[-4]
            year: self.path_elem[-6]  regionID: self.path_elem[-8]

        """
        # If current month/year is end date, grab next regionID
        if self.path_elem[-4] == '05' and self.path_elem[-6] == '2018':
            try:
                self.path_elem[-8] = next(self.regions_itr)
                self.path_elem[-6] = '2015'  # Start in 2015 again
                self.years_itr = iter(self.years)  # Create new year iterator
            except StopIteration:  # All regions have been explored!
                self.path_elem = None
        else:
            try:
                self.path_elem[-4] = next(self.months_itr)
            except StopIteration:  # Months have run out!
                self.path_elem[-4] = '05'  # Start in May again
                self.months_itr = iter(self.months)  # Create new month iterator
            finally:
                if self.path_elem[-4] == '01':  # If January, get next year
                    self.path_elem[-6] = next(self.years_itr)


if __name__ == "__main__":
    # Base Spider name with URI root folder
    base_spider = 'zkbspider_tmpdata'

    # Settings list with custom DOWNLOAD_DELAY:
    # The amount of time (in secs) that the downloader should wait before
    # downloading consecutive pages from the same website. This can be used to
    # throttle the crawling speed to avoid hitting servers too hard. Decimal
    # numbers are supported.

    # Scrapy will introduce a random delay ranging from 0.5 * DOWNLOAD_DELAY to
    # 1.5 * DOWNLOAD_DELAY seconds between consecutive requests to the same
    # domain. If you want to stick to the exact DOWNLOAD_DELAY that you
    # defined, you have to disable RANDOMIZE_DOWNLOAD_DELAY.

    # This script runs 148 concurrent spiders.
    # USER_AGENT limit (using $scrapy bench): ~3000 pages/m | 50 pages/s
    # 3000 pages/m / 148 spiders ~= 20 pages/m per spider MAXIMUM!!
    # @ 5 second delay, delay is b/w 0.5*5 == 2.5s and 7.5s == 1.5*5, or
    # 60 s / 2.5 s/page == 24 pages/m and 60 s/ 7.5 s/page == 8 pages/m.
    # Pretty good interval, rarely will all spiders get above 20 pages/m,
    # especially with AUTOTHROTTLE_ENABLED
    settings = get_project_settings()
    settings.set('DOWNLOAD_DELAY', 5.0)

    page = ZKBPage()  # Create new page element class
    process = CrawlerProcess(settings)  # Create new process

    # Create and add ZKBSpiders to the crawl process
    while page.path_elem is not None:
        # Unique spider name (no other spider can have it) by output folder
        name = (f'{base_spider}/{page.path_elem[-8]}{page.path_elem[-6]}'
                f'{page.path_elem[-4]}')

        # List of URLS for spider to
        start_urls = ['/'.join(page.path_elem)]

        # Add instance of ZKBSpider with scrapy.Spider kwargs
        process.crawl(ZKBSpider(), name=name, start_urls=start_urls)

        # Get next set of path elements
        page.update_path_modifiers()

    # Review spiders before beginning crawl
    for crawler in process.crawlers:
        uri = f"{crawler.spider.name.split('_')[-1]}.csv"
        logging.info(
            f"{crawler.spider.name} will start crawling from "
            f"{crawler.spider.start_urls} and write data to {uri}"
        )

    # Determine if crawl should commence
    begin = input('All Spiders set! Begin crawling? (y/n) >')
    while not (begin == 'y' or begin == 'n'):
        begin = input('All Spiders set! Begin crawling? (y/n) >')

    if begin == 'y':
        process.start()  # script will block here until crawling is finished
        process.stop()  # Shut down all spiders gracefully

    if begin == 'n':
        print('Goodbye! Shutting down...')
