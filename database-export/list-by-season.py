# -*- coding: utf-8 -*-
import os
import re
from datetime import timedelta

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot

os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()

DATE_PLAYING = pywikibot.Timestamp.now() - timedelta(days=365)
DATE_END = pywikibot.Timestamp.now() - timedelta(days=90)

result = dict()
for backlink in pywikibot.ItemPage(datasite, 'Q53').backlinks():  # 動畫
    item = pywikibot.ItemPage(datasite, backlink.title())
    claims = item.get()['claims']
    if 'P29' in claims:  # 首播日期
        date = claims['P29'][0].getTarget().toTimestamp()

        status = 'playing'
        finished = False
        if 'P31' in claims:  # 播放狀態
            if claims['P31'][0].getTarget().id == 'Q58':  # 已完結
                status = 'end'
        if 'P28' in claims and 'P27' in claims and claims['P28'][0].getTarget().amount == claims['P27'][0].getTarget().amount:
            finished = True

        include = False
        if status == 'end' and date > DATE_END and not finished:
            include = True
        if status == 'playing' and date > DATE_PLAYING:
            include = True

        if date.year not in result:
            result[date.year] = []

        result[date.year].append((date.month * 100 + date.day, item.getID(), include))

for year in result:
    print('year', year)

    text = '{{動畫表格列標題}}\n'
    result[year].sort()
    for row in result[year]:
        if row[2]:
            text += '<onlyinclude>{{{{動畫表格列|{}}}}}\n</onlyinclude>'.format(row[1])
        else:
            text += '{{{{動畫表格列|{}}}}}\n'.format(row[1])
    text += '|}\n\n{{各年動畫列表}}'
    text = re.sub(r'</onlyinclude>(\n*)<onlyinclude>', r'\1', text)

    title = '{}年動畫列表'.format(year)
    page = pywikibot.Page(site, title)
    page.text = text
    page.save(summary='產生列表')
