# -*- coding: utf-8 -*-
"""ZKillBoard Killmail and Item Price Extraction Spider

====================IMPORTANT====================READ BELOW====================

CHECK SETTINGS.PY!!!
This is where project wide settings are enabled. Currently enabled settings:
    ROBOTSTXT_OBEY = True
    COOKIES_ENABLED = False
    AUTOTHROTTLE_ENABLED = True
    ^^See https://doc.scrapy.org/en/latest/topics/autothrottle.html
    LOG_LEVEL = 'INFO'
    ^^See https://doc.scrapy.org/en/latest/topics/settings.html#log-level

====================IMPORTANT====================READ ABOVE====================

Extraction Website:
    https://github.com/zKillboard/zKillboard/wiki/API-(Killmails)


Created by: Adam Coscia
Created on: 06-25-2018
Last Modified: 07-17-2018
"""
import json
from datetime import datetime, timedelta
from logging import debug, info, warning

from scrapy import Spider, Request


class ZKBSpider(Spider):
    """Collects Killmails and Item Prices from the ZKillBoard Killmail and
    Price API, and stores the scraped data in CSV format.

    Subclasses `Spider`.
    See https://doc.scrapy.org/en/latest/topics/spiders.html for more info.

    Sends GET Requests to 'https://zkillboard.com/api/kills/' using
    'regionID/#/year/#/month/#/page/#/' path modifiers. Starting from page 1 of
    the initial request month/year/regionID, the spider crawls across the API
    according to the following algorithm:

        1) Parses response from the Killmail API page
           'https://zkillboard.com/api/kills/regionID/#/year/#/month/#/page/#/'
           as a JSON string, converting the string to a list of dicts and
           storing that list to a class data list. If the page returned an
           empty list, the algorithm skips to step 5. Otherwise, proceeds
           as follows:

        2) For each dict (aka single killmail) in the list, a sub-list of
           items that were in the victim's ship is parsed; for each item, the
           price of that item on the date of the killmail's creation (contained
           in the parent dict) is looked up in the spider's class price dict:

               a) If the class price dict has the price for the date
                  requested, that price is multiplied by the quantity_dropped
                  or quantity_destroyed integer supplied with the item info
                  sub-list, and the total price is added to that item's info
                  sub-list in the class data list.

               b) If the class price dict does not have the price for the
                  item on the date requested, the indexes of the item and
                  killmail dicts in each's parent list is recorded, along with
                  the item id and date requested, in a class lookup dict,
                  keyed by the item id, then date, then location indexes.

        3) Once all items have been parsed, and lists updated, the class lookup
           table is attempted to be iterated over by item ID. If the inital
           request to grab the next item ID fails, then no prices need to be
           looked up, and the algorithm proceeeds to step 4. Else, the
           algorithm enters the 'Price Lookup' protocol below:

               a) A GET Request is made to the grabbed item's Price API page
                  at 'https://zkillboard.com/api/prices/item_id/', and the
                  response is parsed and converted from a JSON string to a list
                  of dicts with (date:price) entries.

               b) For each date in the current item's entry of the class lookup
                  table, the price is first sought in the class price dict to
                  avoid parsing duplicate URLS. If the price cannot be found in
                  the class price dict, then each date's price is searched for
                  in the parsed Price API page. If the date is not found on the
                  page, a method is deployed to find the nearest date on the
                  page to the requested date, and that date's price is grabbed.
                  If the price still cannot be obtained, a string with the item
                  ID, date, and URL parsed is used in place of a price.

               c) The value obtained from any of the above processes is added
                  to the class price dict, then to the class data set. The
                  location indexes in the class lookup table for the current
                  item on the current date are used to place the price in each
                  sub-list of the class data list at the location indexes.

               d) The next item is attempted to be grabbed from the class
                  lookup table. If an item is available, the protocol repeats.
                  Else, the protocol ends and the algorithm continues to step 4.

        4) Each dict in the class data list is sent to an Item Pipeline for
           processing, then appended to a CSV output file. The page modifier
           for the Killmail API URL is then incremented by 1, and the algorithm
           repeats back to step 1.

        5) When the class data list is empty, no more pages exist for the
           current /regionID/#/year/#/month/#/ path modifier. At this point,
           the 'Retry Protocol' is enabled. The same URL that produced the
           empty API page will be requested a maximum of 10 times to ensure the
           page did not load slowly. If the page produces data while being
           requested, the algorithm starts back at Step 1. Otherwise, the page
           is assumed to be the end of the API, and the Spider finishes
           crawling.

    """
    # Default name of the spider. Must change b/w instances of spiders!
    name = 'zkbspider'

    # Database of item prices (e.g. itemprice_db[item_id][date] = price)
    # This is shared b/w instances of spiders, so all spiders can access
    # price information!
    itemprice_db = None

    # ======================================================================= #
    # Required Callback Methods
    # ======================================================================= #
    def parse(self, response):
        """Parses the Killmail API response; either implements 'Price-Lookup'
        protocol, or sends scraped killmail data directly to the Item Pipeline
        and requests new Killmail API page, if any are left to scrape.

        """
        # Populate self.price_table and self.data with info from killmail API
        self.parse_killmails(response)
        main_url = response.url

        # self.price_table is non-empty dict, begin 'Price Lookup' Protocol
        if self.price_table:
            lookup = iter(self.price_table)  # Convert price table to iterator
            item_id = next(lookup)  # Get first item
            # For debugging; to enable set LOG_LEVEL to 'DEBUG'
            debug(f"Looking up item ID {item_id}...")
            price_url = f'https://zkillboard.com/api/prices/{item_id}/'
            request = Request(
                url=price_url,
                callback=self.parse_prices,
                dont_filter=True  # Visit a price page multiple times if need be
            )
            request.meta['lookup_table'] = lookup
            request.meta['main_url'] = main_url
            yield request

        # No prices needed to be looked up (prices added already from db), or
        # Killmail API was empty, meaning self.data will be an empty list
        else:
            if self.data:
                # Send data to ProcessBasedExportPipeline for writing to CSV
                for line in self.data:
                    # For debugging; to enable set LOG_LEVEL to 'DEBUG'
                    debug(f"Yielded killmail #{line['killmail_id']}!")
                    yield line

                # Update main URL to new killmail API /page/ while self.data
                next_url = self.update_url(main_url)  # Update URL
                yield Request(url=next_url, callback=self.parse)

            else:  # Follow 'Retry' Protocol in case page loaded slowly
                try:
                    retries = response.meta['retries']
                    retries += 1
                except KeyError:  # Begin 'Retry Protocol'
                    retries = 1

                info(f"No killmails found at {main_url}.")
                info(f"Attempting retry... Attempted Retries so far: "
                     f"{retries}")

                if retries < 10:  # Try it 10 times before quitting
                    request = Request(
                        url=main_url,
                        callback=self.parse,
                        dont_filter=True  # Allow multiple visits to same URL
                    )
                    request.meta['retries'] = retries
                    yield request

                else:
                    info("All pages scraped for "
                         f"{'/'.join(main_url.split('/')[:-2])}/! "
                         "Closing spider...")

    def parse_prices(self, response):
        """Parses the price page of one item, collects price information by
        requested date, stores it to the class database, and adds that price
        info to the class data list. Requests next price page or new killmail
        API page.

        """
        api_prices = json.loads(response.text)
        price_url = response.url
        item_id = price_url.split('/')[-2]

        # Look up price for each date in the price table
        for km_date in self.price_table[item_id]:
            item_info = (item_id, km_date, price_url)  # (str, str, str)
            price = f"Item ID: {item_id}, Date: {km_date}, URL: {price_url}"

            # If price page has already been visited, grab existing entry
            try:
                price = self.__class__.itemprice_db[item_id][km_date]

            # If entry doesn't exist, populate with price info
            except KeyError:
                if api_prices:  # API Prices returned non-empty list
                    try:
                        datetime.strptime(km_date, '%Y-%m-%d')
                        price = api_prices[km_date]  # Grab price from API

                    except ValueError:
                        # If datetime.strptime() throws ValueError, don't
                        # bother getting nearest price or looking km_date up!
                        pass

                    except KeyError:  # No price information for specific date
                        price = self.get_nearest_price(item_info, api_prices)

                # Add price info to database
                try:
                    self.__class__.itemprice_db[item_id][km_date] = \
                        price
                except KeyError:  # item_id has no date dict yet
                    self.__class__.itemprice_db[item_id] = \
                        {km_date: price}

            finally:
                # Finally add the price info to the data set!
                self.add_price(price, item_info)

        # Create new Request for the next item in the lookup table
        try:
            lookup = response.meta['lookup_table']  # Grab lookup table
            item_id = next(lookup)  # Get next item
            # For debugging; to enable set LOG_LEVEL to 'DEBUG'
            debug(f"Looking up item ID {item_id}...")
            price_url = f'https://zkillboard.com/api/prices/{item_id}/'
            request = Request(
                url=price_url,
                callback=self.parse_prices,
                dont_filter=True  # Visit a price page multiple times if need be
            )
            request.meta['lookup_table'] = lookup
            request.meta['main_url'] = response.meta['main_url']
            yield request

        # No more prices to look up, all items have price data
        except StopIteration:
            # Send data to ProcessBasedExportPipeline for writing to CSV
            for line in self.data:
                # For debugging; to enable set LOG_LEVEL to 'DEBUG'
                debug(f"Yielded killmail #{line['killmail_id']}!")
                yield line

            # Update main URL to next killmail API /page/
            next_url = self.update_url(response.meta['main_url'])
            yield Request(url=next_url, callback=self.parse)

    # ======================================================================= #
    # Data-updating Methods
    # ======================================================================= #
    def parse_killmails(self, response):
        """Turns response into a list of Python dicts and adds available price
        information to dicts by killmail date and item id, while compiling a
        list of item id, date, and location of missing price information in
        the dicts.

        Parses `response.text`, a multi-leveled json string, and produces a
        list of dicts containing key-value pairs from the json string. If list
        is non-empty, then for the i-th victim of every killmail, the price of
        the j-th item in their ship's inventory is gathered by the following
        algorithm:

        First, `itemprice_db` is checked to see if the j-th item price
        info already exists; if it does, it uses that price times the quantity
        of that item to calculate total price, then stores total price in the
        j-th item dictionary of the i-th killmail victim.

        If the j-th item id and/or date does not exist in `itemprice_db`,
        then the j-th item id + date, quantity, and location pair (i, j) within
        the list of killmail dicts is stored in `self.price_table`.

        If at any point during parsing of the list of dicts an unchecked
        Exception is caught (one not checked for in the inner try-catch blocks)
        then the entire page of data is thrown out. A list containing one dict
        is returned; the dict contains the proper header field keys and string
        values with the faulty URL and status code recieved. This info is
        also logged to the terminal. The price lookup dict is set empty.

        """
        # Initialize data container (list) for each killmail (dict). Example...
        # data = [ {`first killmail`}, {`second killmail`}, ... ]
        self.data = json.loads(response.text)

        # Initialize price-lookup dict. Example...
        # price_table[item_id][date] = [
        #   (killmail#, item#, quantity),
        #   (...),
        # ]
        # where killmail# and item# are indexes of self.data and
        # self.data[killmail#]['victim']['items'], respectively.
        self.price_table = {}

        # Initialize class Item Price database. Example...
        # itemprice_db[item_id][date] = price
        if self.__class__.itemprice_db is None:
            self.__class__.itemprice_db = {}

        if self.data:  # Page returned non-empty list of killmail dicts
            try:
                # Calculate all prices for the i-th killmail
                for i in range(len(self.data)):
                    date = self.data[i]['killmail_time'].split('T')[0]
                    item_list = self.data[i]['victim']['items']  # list

                    # Calculate price for the j-th item of the i-th killmail
                    for j in range(len(item_list)):
                        item_id = str(item_list[j]['item_type_id'])

                        # Item is either destroyed or dropped, always one of
                        # those keys in the list
                        try:
                            quantity = item_list[j]['quantity_destroyed']
                        except KeyError:
                            try:
                                quantity = item_list[j]['quantity_dropped']
                            except KeyError:  # No quantity info?? :O
                                quantity = 0

                        # Look up item price in class dictionary
                        try:
                            price = self.__class__.itemprice_db[item_id][date]
                            add_price = price

                            # Compute total price of j-th item of i-th killmail
                            # If price wasn't found in price API previously,
                            # price will be a string with info about attempted
                            # scrape. Otherwise, it will be a float
                            if type(price) is float or type(price) is int:
                                add_price = price * quantity

                            # Add price!
                            item_list[j]['total_price'] = add_price
                            # For debugging; to enable set LOG_LEVEL to 'DEBUG'
                            debug(f"Updated: Killmail #{i}, Item #{j},"
                                  f"Price: {price}")

                        # item_id or date not in self.__class__.itemprice_db
                        except KeyError:
                            # Add i-th killmail, j-th item, quantity to lookup
                            lq = (i, j, quantity)
                            try:
                                self.price_table[item_id][date].append(lq)
                            except KeyError:  # item_id or date key error
                                try:
                                    self.price_table[item_id][date] = [lq]
                                except KeyError:  # item_id key error
                                    self.price_table[item_id] = {date: [lq]}

            except Exception as e:  # Exception is caught, didn't account for
                url = response.url
                status = response.status
                # Empty self.price_table so no price page requests made

                # Format killmails list for appending with information
                self.data = [{
                    'killmail_id':
                        f"Unable to retrieve JSON data located at {url}",
                    'killmail_time':
                        f"Recieved status code: {status}",
                    'victim': "ERR",
                    'attackers': "ERR",
                    'solar_system_id': "ERR",
                    'moon_id': "ERR",
                    'war_id': "ERR",
                    'zkb': "ERR"
                }]

                # Log exception thrown, URL and status
                warning(str(e))  # Print Exception to log
                warning(f"Unable to parse JSON data located at: {url}")
                warning(f"Recieved status code: {status}")

    def add_price(self, price, item_info):
        """Adds the price information of a single item, on a single date, to
        all killmails from the scraped page that still need it.

        """
        item_id = item_info[0]
        km_date = item_info[1]

        for location in self.price_table[item_id][km_date]:
            i, j = location[0], location[1]
            add_price = price

            # Compute total price of j-th item of i-th killmail
            # If price wasn't found in price API previously,
            # price will be a string with info about attempted
            # scrape. Otherwise, it will be a float or int
            if type(price) is float or type(price) is int:
                add_price = price * location[2]

            # Add price info to data set :)
            self.data[i]['victim']['items'][j]['total_price'] = add_price
            # For debugging; to enable set LOG_LEVEL to 'DEBUG'
            debug(f"Updated: Killmail #{i}, Item #{j}, Price: {price}")

    # ======================================================================= #
    # Static Calculation Methods
    # ======================================================================= #
    @staticmethod
    def update_url(url):
        """Creates new URL string.

        """
        path_elem = url.split('/')
        path_elem[-2] = str(int(path_elem[-2]) + 1)  # Increase Page Number
        new_url = '/'.join(path_elem)
        info(f"Next page -> {path_elem[-2]} | {new_url}")
        return new_url

    @staticmethod
    def get_nearest_price(item_info, api_prices):
        """Finds the nearest date to the requested date, for a single item
        which does not have price information available for the requested date
        on the API, and collects the nearest date's price information instead.

        """
        price = (f"Item ID: {item_info[0]}, Date: {item_info[1]},"
                 f" URL: {item_info[2]}")
        req_date = datetime.strptime(item_info[1], '%Y-%m-%d')  # Requested Date
        prev_date = req_date
        max_diff = timedelta().max

        # Walk through all dates listed in API and compare to kmail date
        count = 1
        end = len(api_prices)  # If count hits end, use prev date in list
        for date in api_prices:
            try:
                # Keep computing difference b/w req_date and cur_date
                # until smallest difference is found (dates are checked in
                # chronological order, so diff should get smaller until
                # cur_date passes closest date!)
                cur_date = datetime.strptime(date, '%Y-%m-%d')
                diff = req_date - cur_date

                # Difference b/w dates increased above max or end is reached
                if max_diff < diff or count == end:
                    final_date = datetime.strftime(prev_date, '%Y-%m-%d')
                    try:
                        price = api_prices[final_date]
                    finally:  # If price cannot be obtained, still break
                        break
                else:  # Difference b/w dates can be smaller
                    max_diff = diff
                    prev_date = cur_date

            except ValueError:  # key in API could not be processed as date
                pass  # Skip that row!!

            finally:
                count += 1  # Increment counter

        return price
