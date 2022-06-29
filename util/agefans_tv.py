import argparse
import logging
import re

import pywikibot
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class AgefansTv:
    def __init__(self):
        self.ua = UserAgent()

    def getData(self, url):
        headers = {'User-Agent': self.ua.random}
        text = requests.get(url, headers=headers).text
        soup = BeautifulSoup(text, 'html.parser')
        data = {
            'end': False
        }

        data['other_episodes'] = []
        for movurl in soup.find_all('div', {'class': 'movurl'}):
            cnt = len(movurl.findAll('li'))
            data['other_episodes'].append(cnt)
            if movurl.get('style') == 'display:block':
                data['episodes'] = cnt
        if 'episodes' not in data:
            data['episodes'] = max(data['other_episodes'])
        for li in soup.find_all('li', {'class': 'detail_imform_kv'}):
            tag = li.find('span', {'class': 'detail_imform_tag'})
            value = li.find('span', {'class': 'detail_imform_value'})
            if tag and value:
                if '播放状态' in tag.text:
                    if '完结' in value.text:
                        data['end'] = True

        return data

    def updateItem(self, datasite, item):
        itemlabel = item.get()['labels']['zh-tw']
        logging.info('%s %s', item.id, itemlabel)

        claims = item.get()['claims']

        if 'P76' not in claims:
            logging.error('\t No age claims')
            return

        url = claims['P76'][0].getTarget()
        data = self.getData(url)

        # 總集數
        episodesOffset = 0
        if 'P80' in claims['P76'][0].qualifiers:
            episodesOffset = claims['P76'][0].qualifiers['P80'][0].getTarget().amount

        new_episodes = None
        if 'P81' in claims['P76'][0].qualifiers:
            idx = int(claims['P76'][0].qualifiers['P81'][0].getTarget().amount) - 1
            try:
                new_episodes = data['other_episodes'][idx] + episodesOffset
            except IndexError as e:
                logging.error('\t P81 IndexError: %s', idx)
        if new_episodes is None and 'episodes' in data:
            new_episodes = data['episodes'] + episodesOffset

        if new_episodes:
            if 'P27' in claims:
                episodesValue = claims['P27'][0].getTarget()
                old_episodes = episodesValue.amount
                if new_episodes > old_episodes:
                    episodesValue.amount = new_episodes
                    logging.info('\t Update episodes from %s to %s', old_episodes, new_episodes)
                    claims['P27'][0].changeTarget(episodesValue, summary='更新總集數')
            else:
                new_claim = pywikibot.page.Claim(datasite, 'P27')
                new_claim.setTarget(pywikibot.WbQuantity(new_episodes, site=datasite))
                logging.info('\t Add new episodes %s', new_episodes)
                item.addClaim(new_claim, summary='新增總集數')

        # 播放狀態
        if 'P31' in claims:
            if data['end']:
                if claims['P31'][0].getTarget().id != 'Q58':
                    logging.info('\t Update status to end')
                    statusValue = pywikibot.ItemPage(datasite, 'Q58')  # 已完結
                    claims['P31'][0].changeTarget(statusValue, summary='更新播放狀態')
            elif claims['P31'][0].getTarget().id == 'Q57':
                logging.info('\t Update status to playing')
                statusValue = pywikibot.ItemPage(datasite, 'Q56')  # 放送中
                claims['P31'][0].changeTarget(statusValue, summary='更新播放狀態')
        else:
            itemid = 'Q56'
            if data['end']:
                itemid = 'Q58'
            new_claim = pywikibot.page.Claim(datasite, 'P31')
            new_claim.setTarget(pywikibot.ItemPage(datasite, itemid))
            logging.info('\t Add new status')
            item.addClaim(new_claim, summary='新增播放狀態')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    print(AgefansTv().getData(args.url))
