import argparse
import logging
import re

import pywikibot
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


class AcgGamerComTwAcgDetail:
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
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}
        text = requests.get(url, headers=headers).text
        soup = BeautifulSoup(text, 'html.parser')
        data = {}

        box1listA = soup.find('ul', {'class': 'ACG-box1listA'})
        if box1listA:
            episodes = re.search(r'播出集數：(\d+)', box1listA.text)
            if episodes:
                data['episodes'] = int(episodes.group(1))

            year = re.search(r'當地(?:首播|發售)：(\d{4})-(\d{2})-(\d{2})', box1listA.text)
            if year:
                data['year'] = year.group(1) + year.group(2) + year.group(3)

        box1mark = soup.find('p', {'id': 'ACG-box1mark'})

        for img in box1mark.findAll('img'):
            m = re.search(r'TW-(.+?)\.gif', img.get('src'))
            if m:
                data['rating'] = self.RATING_IMG[m.group(1)]
                break

        seasonACG = soup.find('div', {'class': 'seasonACG'})
        if seasonACG:
            firstA = seasonACG.find('a')
            if firstA:
                data['aniGamer'] = 'https:' + firstA.get('href')

        return data

    def _get_wbtime(self, year):
        if len(year) == 4:
            return pywikibot.WbTime(year=int(year), calendarmodel='http://www.wikidata.org/entity/Q1985727')
        if len(year) == 6:
            return pywikibot.WbTime(year=int(year[0:4]), month=int(year[4:6]), calendarmodel='http://www.wikidata.org/entity/Q1985727')
        if len(year) == 8:
            return pywikibot.WbTime(year=int(year[0:4]), month=int(year[4:6]), day=int(year[6:8]), calendarmodel='http://www.wikidata.org/entity/Q1985727')
        return None

    def updateItem(self, datasite, item):
        itemlabel = item.get()['labels']['zh-tw']
        logging.info('%s %s', item.id, itemlabel)

        claims = item.get()['claims']

        if 'P1' not in claims:
            logging.error('\t No acg gamer claims')
            return

        url = claims['P1'][0].getTarget()
        data = self.getData(url)

        episodesOffset = 0
        if 'P80' in claims['P1'][0].qualifiers:
            episodesOffset = claims['P1'][0].qualifiers['P80'][0].getTarget().amount

        # 總集數
        if 'episodes' in data:
            # 已看集數
            if 'P28' not in claims:
                new_claim = pywikibot.page.Claim(datasite, 'P28')
                new_claim.setTarget(pywikibot.WbQuantity(0, site=datasite))
                logging.info('\t Add seen episodes')
                item.addClaim(new_claim, summary='新增已看集數')

            new_episodes = data['episodes'] + episodesOffset
            if 'P27' in claims:
                episodesValue = claims['P27'][0].getTarget()
                old_episodes = episodesValue.amount
                if new_episodes > old_episodes:
                    logging.info('\t Episodes should be updated from %s to %s', old_episodes, new_episodes)
            else:
                new_claim = pywikibot.page.Claim(datasite, 'P27')
                new_claim.setTarget(pywikibot.WbQuantity(new_episodes, site=datasite))
                logging.info('\t Add new episodes %s', new_episodes)
                item.addClaim(new_claim, summary='新增總集數')

        # 播放狀態
        if 'P31' not in claims:
            new_claim = pywikibot.page.Claim(datasite, 'P31')
            new_claim.setTarget(pywikibot.ItemPage(datasite, 'Q58'))
            logging.info('\t Add status')
            item.addClaim(new_claim, summary='新增播放狀態')

        # 年份
        if 'year' in data:
            if 'P29' in claims:
                if claims['P29'][0].getTarget().precision < 11:
                    wbtime = self._get_wbtime(data['year'])
                    if wbtime:
                        logging.info('\t Update year to %s', data['year'])
                        claims['P29'][0].changeTarget(wbtime, summary='更新年份')
            else:
                wbtime = self._get_wbtime(data['year'])
                if wbtime:
                    new_claim = pywikibot.page.Claim(datasite, 'P29')
                    new_claim.setTarget(wbtime)
                    logging.info('\t Add new year %s', data['year'])
                    item.addClaim(new_claim, summary='新增年份')

        # 台灣分級
        if 'rating' in data:
            rating_exists = False
            if 'P23' in claims:
                for claim in claims['P23']:
                    if claim.getTarget().id == self.RATING_ITEM[data['rating']]:
                        rating_exists = True

                        if len(claim.sources) == 0:
                            rating_source = pywikibot.page.Claim(datasite, 'P1')
                            rating_source.setTarget(url)
                            logging.info('\t Add source to rating')
                            claim.addSource(rating_source)
                    else:
                        if len(claim.sources) > 0 and 'P1' in claim.sources[0] and claim.sources[0]['P1'][0].getTarget() == url:
                            rating_exists = True
                            logging.info('\t Update ranking to %s', data['rating'])
                            claim.changeTarget(pywikibot.ItemPage(datasite, self.RATING_ITEM[data['rating']]), summary='更新台灣分級')

            if not rating_exists:
                new_claim = pywikibot.page.Claim(datasite, 'P23')
                new_claim.setTarget(pywikibot.ItemPage(datasite, self.RATING_ITEM[data['rating']]))

                rating_source = pywikibot.page.Claim(datasite, 'P1')
                rating_source.setTarget(url)
                new_claim.addSource(rating_source)

                logging.info('\t Add new rating %s', data['rating'])
                item.addClaim(new_claim, summary='新增台灣分級')

        # 動畫瘋影片網址
        if 'aniGamer' in data:
            if 'P34' not in claims:
                new_claim = pywikibot.page.Claim(datasite, 'P34')
                new_claim.setTarget(data['aniGamer'])
                logging.info('\t Add new ani.gamer url %s', data['aniGamer'])
                item.addClaim(new_claim, summary='新增巴哈姆特動畫瘋連結')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    args = parser.parse_args()
    print(AcgGamerComTwAcgDetail().getData(args.url))
