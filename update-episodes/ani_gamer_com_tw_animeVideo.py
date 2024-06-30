# -*- coding: utf-8 -*-
import argparse
import importlib
import logging
import os
import difflib
import re
import sys
from bs4 import BeautifulSoup

import requests
from fake_useragent import UserAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['PYWIKIBOT_DIR'] = BASE_DIR
import pywikibot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
)

sys.path.append(os.path.dirname(BASE_DIR))
animeSite = (importlib.import_module('util.ani_gamer_com_tw_animeVideo', 'AniGamerComTwAnimeVideo')
             .AniGamerComTwAnimeVideo())

site = pywikibot.Site()
site.login()
datasite = pywikibot.DataSite('myacg')


def main(title=None):
    title_map = {}
    for backlink in pywikibot.ItemPage(datasite, 'Q56').backlinks(namespaces=[120]):  # 放送中
        item = pywikibot.ItemPage(datasite, backlink.title())
        title_map[item.get()['labels']['zh-tw']] = backlink.title()
    for backlink in pywikibot.ItemPage(datasite, 'Q57').backlinks(namespaces=[120]):  # 尚未放送
        item = pywikibot.ItemPage(datasite, backlink.title())
        title_map[item.get()['labels']['zh-tw']] = backlink.title()
    if title:
        item = pywikibot.ItemPage(datasite, title)
        title_map[item.get()['labels']['zh-tw']] = title

    url = 'https://ani.gamer.com.tw/'
    ua = UserAgent()
    headers = {'User-Agent': ua.random}
    text = requests.get(url, headers=headers).text

    soup = BeautifulSoup(text, 'html.parser')
    for card in reversed(soup.find('div', {'class': 'timeline-ver'}).find_all('a', {'class': 'anime-card-block'})):
        anime_name = card.find('div', {'class': 'anime-name'}).find('p').text
        episode_p = card.find('div', {'class': 'anime-episode'}).find('p')

        anime_episode = None
        if episode_p:
            m = re.search(r'^第(\d+)集$', episode_p.text)
            if m:
                anime_episode = int(m.group(1))
            m = re.search(r'^第(\d+)\.5集$', episode_p.text)
            if m:
                anime_episode = int(m.group(1)) + 1
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
    parser = argparse.ArgumentParser()
    parser.add_argument('title', nargs='?')
    args = parser.parse_args()
    main(args.title)
