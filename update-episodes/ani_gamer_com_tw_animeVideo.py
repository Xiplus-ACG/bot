# -*- coding: utf-8 -*-
import importlib
import logging
import os
import difflib
import re
import sys
from bs4 import BeautifulSoup

import requests
from fake_useragent import UserAgent

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
)

sys.path.append('..')
animeSite = (importlib.import_module('util.ani_gamer_com_tw_animeVideo', 'AniGamerComTwAnimeVideo')
             .AniGamerComTwAnimeVideo())

site = pywikibot.Site()
site.login()
datasite = site.data_repository()


def main():
    title_map = {}
    for backlink in pywikibot.ItemPage(datasite, 'Q56').backlinks(namespaces=[120]):  # 放送中
        item = pywikibot.ItemPage(datasite, backlink.title())
        title_map[item.get()['labels']['zh-tw']] = backlink.title()
    for backlink in pywikibot.ItemPage(datasite, 'Q57').backlinks(namespaces=[120]):  # 尚未放送
        item = pywikibot.ItemPage(datasite, backlink.title())
        title_map[item.get()['labels']['zh-tw']] = backlink.title()

    url = 'https://ani.gamer.com.tw/'
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    text = requests.get(url, headers=headers).text

    soup = BeautifulSoup(text, 'html.parser')
    for card in soup.find_all('a', {'class': 'anime-card-block'}):
        anime_name = card.find('div', {'class': 'anime-name'}).find('p').text
        episode_p = card.find('div', {'class': 'anime-episode'}).find('p')

        anime_episode = None
        if episode_p:
            m = re.search(r'^第(\d+)集$', episode_p.text)
            if m:
                anime_episode = int(m.group(1))
        else:
            anime_episode = 1

        matches = difflib.get_close_matches(anime_name, title_map.keys())
        if len(matches) > 0:
            animeSite.updateItem(
                datasite,
                pywikibot.ItemPage(datasite, title_map[matches[0]]),
                {
                    'episodes': anime_episode,
                }
            )


if __name__ == "__main__":
    main()
