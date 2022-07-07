# -*- coding: utf-8 -*-
import os

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()

platforms = {
    'all': '所有',
    'P34': '動畫瘋',
}

result = {}
for platform in platforms:
    result[platform] = {
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
    cur_result = {
        'seasons': 0,
        'normalized_seasons': 0,
        'episodes': 0,
        'minutes': 0,
    }
    if 'P27' in claims:  # 總集數
        episodes = int(claims['P27'][0].getTarget().amount)
    if 'P28' in claims:  # 已看集數
        seen = int(claims['P28'][0].getTarget().amount)
    if 'P25' in claims:  # 每集時間
        length = float(claims['P25'][0].getTarget().amount)

    if seen > 0:
        cur_result['seasons'] = 1
        cur_result['episodes'] = seen
        if episodes >= 12:
            cur_result['normalized_seasons'] += round(episodes // 12)
        elif episodes >= 3:
            cur_result['normalized_seasons'] += 1
    cur_result['minutes'] += length * seen

    for platform in platforms:
        if platform == 'all' or platform in claims:
            for key in cur_result:
                result[platform][key] += cur_result[key]

    # print('{} {}/{}, {} minutes'.format(name, seen, episodes, length))

text_list = []
for platform, pl_result in result.items():
    temp = ''
    if platform != 'all':
        temp += platforms[platform] + '\n'
    temp += '* 季數：{}\n'.format(pl_result['seasons'])
    temp += '* 正規化季數：{}\n'.format(pl_result['normalized_seasons'])
    temp += '* 集數：{}\n'.format(pl_result['episodes'])
    temp += '* 時數：{}分鐘 = {}小時 = {}天\n'.format(
        pl_result['minutes'], round(pl_result['minutes'] / 60), round(pl_result['minutes'] / 60 / 24)
    )
    text_list.append(temp)

text = '----\n'.join(text_list)

page = pywikibot.Page(site, 'Project:統計')
page.text = text
page.save(summary='產生統計')
