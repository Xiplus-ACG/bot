# -*- coding: utf-8 -*-
import os

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()

result = dict()
for backlink in pywikibot.ItemPage(datasite, 'Q53').backlinks():  # 動畫
    item = pywikibot.ItemPage(datasite, backlink.title())
    claims = item.get()['claims']
    if 'P29' in claims:
        date = claims['P29'][0].getTarget().toTimestamp()
        if date.year not in result:
            result[date.year] = []

        result[date.year].append((date.month * 100 + date.day, item.getID()))

for year in result:
    print('year', year)

    text = '{{動畫表格列標題}}\n'
    result[year].sort()
    for row in result[year]:
        text += '{{{{動畫表格列|{}}}}}\n'.format(row[1])
    text += '|}\n\n{{各年動畫列表}}'

    title = '{}年動畫列表'.format(year)
    page = pywikibot.Page(site, title)
    page.text = text
    page.save(summary='產生列表')
