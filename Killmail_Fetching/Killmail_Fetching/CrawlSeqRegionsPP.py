# -*- coding: utf-8 -*-
"""ZKillBoard Killmail and Item Price Extraction Script (Sequential)

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

This script scrapes all pages of a given month/year URL path, and SEQUENTIALLY
queues regions to be scraped. Thus, 37 concurrent spiders will each crawl a
unique month from 05-2015 to 05-2018 for a single regionID. Then, the script
will establish the next 37 spiders to concurrently crawl the same time span for
the next regionID, until all regions have been scraped.

Extraction API:
    https://github.com/zKillboard/zKillboard/wiki/API-(Killmails)

Created by: Adam Coscia
Created on: 07-12-2018
Last Modified: 07-17-2018
"""
import logging

from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from twisted.internet import reactor, defer

from spiders.zkbspider import ZKBSpider


class ZKBPage(object):
    """Creates and updates path modifiers used in requests made by spiders.

    URLS for each spider are relative to 4 sets of path element:identifier
    strings > RegionID : ``str`` | year : ``str`` | month : ``str`` |
    page : ``str``

    Every time `self.update_path_modifiers` is called, `self.path_elem` is
    updated with the next month and/or year sequentially from the previous
    month/year. If end date is reached, self.path_elem is set to None.

    Dates are from 05/2015 to 05/2018.

    """

    def __init__(self, region_id):
        # Lists of path element strings to populate new URLs string with
        self.months = ['06', '07', '08', '09', '10', '11', '12', '01', '02',
                       '03', '04']
        self.months_itr = iter(self.months)
        self.years = ['2016', '2017', '2018']
        self.years_itr = iter(self.years)

        # Starting path elements
        self.path_elem = [
            'https:', '', 'zkillboard.com', 'api', 'kills', 'region_id',
            region_id, 'year', '2015', 'month', '05', 'page', '1', ''
        ]

    def update_path_modifiers(self):
        """Updates instance path elements until end date is reached.

        Important fields:
            page: self.path_elem[-2]  month: self.path_elem[-4]
            year: self.path_elem[-6]  regionID: self.path_elem[-8]

        """
        # If current month/year is end date, stop generating path elements
        if self.path_elem[-4] == '05' and self.path_elem[-6] == '2018':
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


class ZKBCrawlingManager(object):
    """Manages the queueing of spiders by regionID to the CrawlRunner object.

    """
    def __init__(self, runner):
        self.runner = runner
        # Region iterable
        self.regions = iter(['10000002', '10000016', '10000033', '10000069'])
        # Base Spider name with URI root folder
        self.base_spider = 'zkbspider_tmpdata'

    def generate_spiders(self):
        """Creates spiders from the ZKBSpider class to be sent crawling by
        the CrawlRunner object.

        Supplies each spider with a unique name, a list of starting URLS to
        crawl, and adds each spider to a dict with their name as the key.

        """
        spiders = {}  # Instantiate empty dict to populate with spiders

        try:
            region_id = next(self.regions)
            page = ZKBPage(region_id)  # Create new page element class

            # Create and add ZKBSpiders to the crawl
            while page.path_elem is not None:
                # Unique spider name by output folder
                name = (f'{self.base_spider}/{region_id}{page.path_elem[-6]}'
                        f'{page.path_elem[-4]}')

                # List of URLS for spider to crawl
                start_urls = ['/'.join(page.path_elem)]

                # Add instance of ZKBSpider with scrapy.Spider kwargs
                spiders[name] = {'spider': ZKBSpider(),
                                 'start_urls': start_urls}

                # Get next set of path elements
                page.update_path_modifiers()

        except StopIteration:  # No more spiders to be generated!
            pass

        finally:
            return spiders

    @defer.inlineCallbacks
    def begin_crawling(self):
        """Controls the crawling process for all spiders created.

        Calls `generate_spiders()` to get a list of spider instances to review.
        If the user supplies the shell with a 'y', each spider is sent to the
        `CrawlRunner` object to become a `Crawler` and sent crawling. A
        `Deferred` is chained to the completion of all spiders sent crawling
        in each batch; upon its firing, the next batch of spiders is generated
        and queued for reivew and the process repeats until no spiders are
        generated.

        """
        # Generate first round of Spiders for crawling
        spiders = crawling_manager.generate_spiders()

        while spiders:
            # Review spiders before beginning crawl
            for spider_name in spiders:
                uri = f"{spider_name.split('_')[-1]}.csv"
                logging.info(
                    f"{spider_name} will start crawling from "
                    f"{spiders[spider_name]['start_urls']} and write data to"
                    f"{uri}"
                )

            # Determine if the scraping should continue at this breakpoint
            begin = input('All Spiders set! Begin crawling? (y/n) >')
            while not (begin == 'y' or begin == 'n'):
                begin = input('All Spiders set! Begin crawling? (y/n) >')

            if begin == 'n':
                print('Goodbye! Shutting down...')
                return  # Kill the generator early

            # Set each spider crawling!
            for spider_name in spiders:
                self.runner.crawl(
                    spiders[spider_name]['spider'],
                    name=spider_name,
                    start_urls=spiders[spider_name]['start_urls']
                )

            # Callback chained to the execution of all spiders in the runner
            yield self.runner.join()

            # Generate next round of Spiders for crawling
            spiders = crawling_manager.generate_spiders()


if __name__ == "__main__":
    # Settings list with custom DOWNLOAD_DELAY:
    # The amount of time (in secs) that the downloader should wait before
    # downloading consecutive pages from the same website. This can be used to
    # throttle the crawling speed to avoid hitting servers too hard. Decimal
    # numbers are supported.

    # Scrapy will introduce a random delay ranging from 0.5 * DOWNLOAD_DELAY to
    # 1.5 * DOWNLOAD_DELAY seconds between consecutive requests to the same
    # domain. If you want to stick to the exact DOWNLOAD_DELAY that you
    # defined, you have to disable RANDOMIZE_DOWNLOAD_DELAY.

    # This script runs 37 concurrent spiders 4 times.
    # USER_AGENT limit (using $scrapy bench): ~3000 pages/m | 50 pages/s
    # 3000 pages/m / 37 spiders ~= 81 pages/m per spider MAXIMUM!!
    # @ 0.75s delay, delay is b/w 0.5*0.66 == 0.33s and 0.99s == 1.5*0.66, or
    # 60 s / 0.33 s/page == 182 pages/m and 61 pages/m == 60 s/ 0.99 s/page.
    # Spiders will try to reach (fluctuate) around 60/0.66 == 90 pages/m, with
    # Autothrottle spiders usually get around 75 pages/m
    settings = get_project_settings()
    settings.set('DOWNLOAD_DELAY', 0.7)

    configure_logging()  # Set up logging machine
    r = CrawlerRunner(settings)  # Create new runner

    # Create a crawling manager
    crawling_manager = ZKBCrawlingManager(r)

    try:
        crawling_manager.begin_crawling()  # Generate Spiders for crawling
        reactor.run()  # Start the Reactor
    except StopIteration:  # Early return call from entering 'n' in prompt
        pass
    finally:
        if reactor.running:
            reactor.stop()  # Shutdown the reactor
