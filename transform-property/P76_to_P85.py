# -*- coding: utf-8 -*-
import argparse
import os
import re

os.environ['PYWIKIBOT_DIR'] = os.path.dirname(os.path.realpath(__file__))
import pywikibot


site = pywikibot.Site()
site.login()
datasite = pywikibot.DataSite('myacg')


def changeP76toP85(title):
    title = title.replace('Item:', '')
    title = title.replace('Property:', '')
    print(title)

    if title[0] == 'Q':
        myitem = pywikibot.ItemPage(datasite, title)
    elif title[0] == 'P':
        myitem = pywikibot.PropertyPage(datasite, title)
    else:
        print('\t Not Wikibase page')
        return

    myitem.get()
    data = myitem.toJSON()

    if 'P85' not in myitem.claims:
        new_claim = pywikibot.page.Claim(datasite, 'P85')
        url = myitem.claims['P76'][0].getTarget()
        m = re.search(r'^https?://www\.age.*/(?:detail|play)/(\d+)(?:/.+)?$', url)
        if not m:
            print('\t Not agefans url')
            return
        newValue = m.group(1)
        print('\t', newValue)
        new_claim.setTarget(newValue)
        print('\t', new_claim)
        data['claims']['P85'] = [new_claim.toJSON()]
        data['claims']['P76'][0]['remove'] = ''
        myitem.editEntity(data, summary='轉換屬性')


def main():
    P76 = pywikibot.PropertyPage(datasite, 'P76')

    for backlink in P76.backlinks():
        changeP76toP85(backlink.title())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('title', nargs='?')
    args = parser.parse_args()
    if args.title:
        changeP76toP85(args.title)
    else:
        main()
