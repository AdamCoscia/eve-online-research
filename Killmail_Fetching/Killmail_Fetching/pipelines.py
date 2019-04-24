# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import logging
from scrapy.exporters import CsvItemExporter


class ProcessBasedExportPipeline(object):
    """Distribute each killmail to a unique CSV file according to which spider
    sent the killmail.

    """

    def __init__(self):
        self.file = None
        self.fields = None
        self.exporter = None

    def open_spider(self, spider):
        # Unique filepath based on spider's name
        uri = f"{spider.name.split('_')[-1]}.csv"
        self.file = open(uri, 'wb')
        # CSV Header Fields (dict keys) accepted by the pipeline
        self.fields = ['killmail_id', 'killmail_time', 'victim', 'attackers',
                       'solar_system_id', 'moon_id', 'war_id', 'zkb']
        # Use built-in exporter with pre-defined header fields
        self.exporter = CsvItemExporter(self.file, include_headers_line=True,
                                        fields_to_export=self.fields)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        # item is a single killmail dict, example:
        # item = {
        #   'killmail_id': 12345678,
        #   'killmail_time': 2000-01-01T00:00:00Z,
        #   'victim' : { `victim information` },
        #   'attackers': { `attacker information` },
        #   'solar_system': 12345678,
        #   'moon_id': 12345678,
        #   'war_id': 123456
        #   'zkb': { `ZKB quick info on killmail` }
        # }
        for field in item:
            if field not in self.fields:
                logging.warning(
                    f"UNEXPECTED FIELD ({field}) IN KILLMAIL "
                    f"{item['killmail_id']}_{item['killmail_time']}. REMOVING "
                    f"FIELD..."
                )
                del item[field]
        self.exporter.export_item(item)
        return item
