# -*- coding: utf-8 -*-
import os

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()

result = {
    'seasons': 0,
    'normalized_seasons': 0,
    'episodes': 0,
    'minutes': 0,
}
for backlink in pywikibot.ItemPage(datasite, 'Q53').backlinks():  # 動畫
    item = pywikibot.ItemPage(datasite, backlink.title())
    name = item.get()['labels']['zh-tw']
    claims = item.get()['claims']

    episodes = 0
    seen = 0
    length = 0
    if 'P27' in claims:  # 總集數
        episodes = int(claims['P27'][0].getTarget().amount)
    if 'P28' in claims:  # 已看集數
        seen = int(claims['P28'][0].getTarget().amount)
        if seen > 0:
            result['seasons'] += 1
            result['episodes'] += seen
            if episodes >= 12:
                result['normalized_seasons'] += round(episodes // 12)
            elif episodes >= 3:
                result['normalized_seasons'] += 1
    if 'P25' in claims:  # 每集時間
        length = float(claims['P25'][0].getTarget().amount)

    result['minutes'] += length * seen
    # print('{} {}/{}, {} minutes'.format(name, seen, episodes, length))

text = ''
text += '* 季數：{}\n'.format(result['seasons'])
text += '* 正規化季數：{}\n'.format(result['normalized_seasons'])
text += '* 集數：{}\n'.format(result['episodes'])
text += '* 時數：{}分鐘 = {}小時 = {}天\n'.format(
    result['minutes'], round(result['minutes'] / 60), round(result['minutes'] / 60 / 24)
)

page = pywikibot.Page(site, 'Project:統計')
page.text = text
page.save(summary='產生統計')
