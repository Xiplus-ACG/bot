import argparse
import logging
import re

import pywikibot
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class AniGamerComTwAnimeVideo:
    RATING_IMG = {
        'ALL': 0,
        '6TO12': 6,
        '12TO18': 12,
        '15TO18': 15,
        '18UP': 18,
    }
    RATING_ITEM = {
        0: 'Q46',
        6: 'Q47',
        12: 'Q48',
        15: 'Q49',
        18: 'Q50',
    }

    def __init__(self):
        self.ua = UserAgent()

    def getData(self, url):
        headers = {'User-Agent': self.ua.random}
        text = requests.get(url, headers=headers).text
        data = {
            'removed': False,
            'episodes': [],
            'other_episodes': {},
        }

        if '目前無此動畫或動畫授權已到期！' in text:
            data['removed'] = True
            return data

        soup = BeautifulSoup(text, 'html.parser')

        season = soup.find('section', {'class': 'season'})
        if season is None:
            data['episodes'].append('')
        else:
            if season.find('p'):
                data['other_episodes'] = {}
                for p in season.findAll('p'):
                    ul = p.findNext('ul')
                    if ul:
                        data['other_episodes'][p.text] = []
                        for li in ul.findAll('li'):
                            data['episodes'].append(li.text)
                            data['other_episodes'][p.text].append(li.text)
            else:
                for ul in season.findAll('ul'):
                    for li in ul.findAll('li'):
                        data['episodes'].append(li.text)

        rating = soup.find('div', {'class': 'rating'})
        if rating:
            src = rating.find('img').get('src')
            m = re.search(r'TW-(.+?)\.gif', src)
            if m:
                data['rating'] = self.RATING_IMG[m.group(1)]

        data_intro = soup.find('div', {'class': 'data_intro'})
        if data_intro:
            linkdiv = data_intro.find('div', {'class': 'link'})
            if linkdiv:
                for link in linkdiv.findAll('a'):
                    if link.text == '作品資料':
                        data['acg_link'] = link.get('href')
                        if data['acg_link'].startswith('//'):
                            data['acg_link'] = 'https:' + data['acg_link']

        return data

    def updateItem(self, datasite, item, data):
        itemlabel = item.get()['labels']['zh-tw']
        logging.info('%s %s', item.id, itemlabel)

        claims = item.get()['claims']

        if 'P34' not in claims:
            logging.warning('\t No anime gamer claims')
            return

        url = claims['P34'][0].getTarget()

        episodesOffset = 0
        if 'P80' in claims['P34'][0].qualifiers:
            episodesOffset = claims['P34'][0].qualifiers['P80'][0].getTarget().amount

        # 移除巴哈姆特動畫瘋連結
        if 'removed' in data and data['removed']:
            logging.info('\tRemove anime gamer link')
            item.removeClaims(claims['P34'], summary='影片已移除')
            return

        # 從巴哈姆特動畫瘋匯入巴哈姆特作品資料
        if 'acg_link' in data and 'P1' not in claims:
            new_claim = pywikibot.page.Claim(datasite, 'P1')
            new_claim.setTarget(data['acg_link'])
            logging.info('\t Add acg gamer link %s', data['acg_link'])
            item.addClaim(new_claim)

        # 台灣分級
        if 'rating' in data:
            rating_exists = False
            if 'P23' in claims:
                for claim in claims['P23']:
                    if claim.getTarget().id == self.RATING_ITEM[data['rating']]:
                        rating_exists = True

                        if len(claim.sources) == 0:
                            rating_source = pywikibot.page.Claim(datasite, 'P34')
                            rating_source.setTarget(url)
                            logging.info('\t Add source to rating')
                            claim.addSource(rating_source)

            if not rating_exists:
                new_claim = pywikibot.page.Claim(datasite, 'P23')
                new_claim.setTarget(pywikibot.ItemPage(datasite, self.RATING_ITEM[data['rating']]))

                rating_source = pywikibot.page.Claim(datasite, 'P34')
                rating_source.setTarget(url)
                new_claim.addSource(rating_source)

                logging.info('\t Add new rating %s', data['rating'])
                item.addClaim(new_claim, summary='新增台灣分級')

        # 總集數
        if 'episodes' in data:
            new_episodes = data['episodes']
            new_episodes += episodesOffset
            if 'P27' in claims:
                episodesValue = claims['P27'][0].getTarget()
                old_episodes = episodesValue.amount
                if new_episodes > old_episodes:
                    episodesValue.amount = new_episodes
                    logging.info('\t Update episodes from %s to %s', old_episodes, new_episodes)
                    claims['P27'][0].changeTarget(episodesValue, summary='更新總集數')
                elif new_episodes < old_episodes:
                    logging.warning('\t New episodes %s less than old episodes %s', new_episodes, old_episodes)
            else:
                new_claim = pywikibot.page.Claim(datasite, 'P27')
                new_claim.setTarget(pywikibot.WbQuantity(new_episodes, site=datasite))
                logging.info('\t Add new episodes %s', new_episodes)
                item.addClaim(new_claim, summary='新增總集數')

        # 播放狀態
        if 'P31' in claims and claims['P31'][0].getTarget().id == 'Q57':
            logging.info('\t Update status to playing')
            statusValue = pywikibot.ItemPage(datasite, 'Q56')
            claims['P31'][0].changeTarget(statusValue, summary='更新播放狀態')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    print(AniGamerComTwAnimeVideo().getData(args.url))
