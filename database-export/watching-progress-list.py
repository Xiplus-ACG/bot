# -*- coding: utf-8 -*-
import os

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


os.environ['TZ'] = 'UTC'

site = pywikibot.Site()
site.login()
datasite = site.data_repository()


natures = {
    'Q53': '動畫',
    'Q1058': '電視劇',
}


def get_backlinks(qid):
    res = set()
    for backlink in pywikibot.ItemPage(datasite, qid).backlinks(namespaces=[120]):
        item = pywikibot.ItemPage(datasite, backlink.title())
        res.add(int(item.id[1:]))
    return res


ended = get_backlinks('Q58')  # 已完結

for nature_id, nature_name in natures.items():
    video_ids = sorted(get_backlinks(nature_id).intersection(ended))

    text_plan = '{{動畫表格列標題}}\n'
    text_watching = '{{動畫表格列標題}}\n'
    for video_id in video_ids:
        item = pywikibot.ItemPage(datasite, 'Q{}'.format(video_id))
        claims = item.get()['claims']

        seen = 0
        if 'P28' in claims:
            seen = claims['P28'][0].getTarget().amount
        episodes = 0
        if 'P27' in claims:
            episodes = claims['P27'][0].getTarget().amount

        if seen == 0:
            text_plan += '{{{{動畫表格列|{}}}}}\n'.format(item.id)
        elif seen > 0 and seen != episodes:
            text_watching += '{{{{動畫表格列|{}}}}}\n'.format(item.id)

    text_plan += '|}'
    text_watching += '|}'
    if nature_id == 'Q53':
        text_plan += '\n\n{{各年動畫列表}}'
        text_watching += '\n\n{{各年動畫列表}}'

    page_plan = pywikibot.Page(site, 'Project:尚未開始看的{}'.format(nature_name))
    page_plan.text = text_plan
    pywikibot.showDiff(page_plan.text, text_plan)
    page_plan.save(summary='產生列表')

    page_watching = pywikibot.Page(site, 'Project:尚未看完的{}'.format(nature_name))
    page_watching.text = text_watching
    pywikibot.showDiff(page_watching.text, text_watching)
    page_watching.save(summary='產生列表')
