# -*- coding: utf-8 -*-
import os
import re

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = pywikibot.DataSite('myacg')

title = 'ACG:首頁'
page = pywikibot.Page(site, title)
text = page.text
itemIds = re.findall(r'{{動畫表格列\|(Q\d+)}}', text)
for itemId in itemIds:
    item = pywikibot.ItemPage(datasite, itemId)
    claims = item.get()['claims']
    if 'P31' not in claims or claims['P31'][0].getTarget().id != 'Q58':
        continue
    if 'P28' not in claims or 'P27' not in claims:
        continue

    seen = claims['P28'][0].getTarget().amount
    episodes = claims['P27'][0].getTarget().amount
    if seen == episodes:
        text = re.sub(r'{{{{動畫表格列\|{0}}}}}\n?'.format(item.id), '', text)

page.text = text
page.save(summary='移除已看完項目')
