# -*- coding: utf-8 -*-
import argparse
import importlib
import logging
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PYWIKIBOT_DIR'] = BASE_DIR
import pywikibot


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
)

sys.path.append(os.path.dirname(BASE_DIR))
animeSite = (importlib.import_module('util.acg_gamer_com_tw_acgDetail', 'AcgGamerComTwAcgDetail')
             .AcgGamerComTwAcgDetail())

site = pywikibot.Site()
site.login()
datasite = pywikibot.DataSite('myacg')


def importAcgGamerLink(title):
    myitem = pywikibot.ItemPage(datasite, title)

    animeSite.updateItem(datasite, myitem)


def main():
    for backlink in pywikibot.PropertyPage(datasite, 'P1').backlinks(namespaces=[120]):  # 巴哈姆特作品資料
        myitem = pywikibot.ItemPage(datasite, backlink.title())
        claims = myitem.get()['claims']
        if 'P23' not in claims:
            importAcgGamerLink(backlink.title())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('title', nargs='?')
    args = parser.parse_args()
    if args.title is None:
        main()
    else:
        importAcgGamerLink(args.title)
