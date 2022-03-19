# -*- coding: utf-8 -*-
import os

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()

for backlink in pywikibot.ItemPage(datasite, 'Q53').backlinks():  # 動畫
    item = pywikibot.ItemPage(datasite, backlink.title())
    name = item.get()['labels']['zh-tw']
    claims = item.get()['claims']

    seen = 0
    if 'P28' in claims:  # 已看集數
        seen = int(claims['P28'][0].getTarget().amount)
    if seen == 0:
        continue
    episodes = 0
    if 'P27' in claims:  # 總集數
        episodes = int(claims['P27'][0].getTarget().amount)

    if 'P25' not in claims:  # 每集時間
        print('{} {} {}/{} {}'.format(item.title(), name, seen, episodes, item.full_url()))
        length = input('> ')
        try:
            length = float(length)
            if length == int(length):
                length = int(length)
        except Exception:
            length = 0
        if length > 0:
            new_claim = pywikibot.page.Claim(datasite, 'P25')
            new_claim.setTarget(pywikibot.WbQuantity(length, site=datasite, unit='https://xiplus.ddns.net/entity/Q54'))
            item.addClaim(new_claim, summary='新增每集時間')
