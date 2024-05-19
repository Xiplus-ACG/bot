# -*- coding: utf-8 -*-
import argparse
import importlib
import logging
import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PYWIKIBOT_DIR'] = BASE_DIR
import pywikibot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
)

sys.path.append(os.path.dirname(BASE_DIR))
animeSite = importlib.import_module('util.anime1_me', 'Anime1Me').Anime1Me()

site = pywikibot.Site()
site.login()
datasite = pywikibot.DataSite('myacg')


def updateEpisodes(title):
    myitem = pywikibot.ItemPage(datasite, title)

    animeSite.updateItem(datasite, myitem)


def main():
    for backlink in pywikibot.ItemPage(datasite, 'Q56').backlinks(namespaces=[120]):  # 放送中
        try:
            updateEpisodes(backlink.title())
        except Exception:
            logging.error(traceback.format_exc())
    for backlink in pywikibot.ItemPage(datasite, 'Q57').backlinks(namespaces=[120]):  # 尚未放送
        try:
            updateEpisodes(backlink.title())
        except Exception:
            logging.error(traceback.format_exc())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('title', nargs='?')
    args = parser.parse_args()
    if args.title is None:
        main()
    else:
        updateEpisodes(args.title)
