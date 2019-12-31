from test import NotionWebsiteBuilder
from secret import token
import regex as re

import os

website = NotionWebsiteBuilder(token_v2=token)

sitedata = {
    'wordcount': 0,
    'pagecount': 0,
    'glossary': {}
}

def addGlossaryItem(data):
    match = re.match(r'(.+)\((.+)\):(.+)', data['rawtext'])
    if match != None:
        item, category, glossary_text = match.groups()
        if category not in sitedata['glossary']:
            sitedata['glossary'][category] = {}
        
        sitedata['glossary'][category.strip()][item.strip()] = glossary_text.strip()


arr = []
def countwords(data):
    if data['type'] not in ['code', 'callout'] and 'rawtext' in data:
        sitedata['wordcount'] += len(data['rawtext'].split())

def countpages(data):
    sitedata['pagecount'] += 1

website.listen('blocks/callout/🔮', addGlossaryItem)
website.listen('blocks', countwords)
website.listen('pages', countpages)


website.addCollection('pages', 'https://www.notion.so/eidka/b539082b0b02490580f7fd5872d1798e?v=38b84447673746abb18521983b30abe0', folder='')
website.addCollection('blog', 'https://www.notion.so/eidka/7dc1a478d8274055a1f7b9f04d29057b?v=d4fb4101b07649cd95c5fcf63cc7c232')
website.addCollection('wiki', 'https://www.notion.so/eidka/df41aba6463b4d8cb3b6c2b40b0de634?v=bcea2c4e405441399470592c2a096be9')
website.addCollection('projects', 'https://www.notion.so/eidka/a1b4d1e913f0400d8baf0581caaedea7?v=52e1aaf92d1b4875a16ca2d09c7c60c8')

for page in website.cache.values():
    page['flags'] = {
        'new': False,
        'updated': False
    }

from datetime import datetime
website.env.globals['fromiso'] = datetime.fromisoformat

website.render({
    'site': sitedata
})

# generate glossary in .ndtl format for Merveille's collaborative wiki
with open(os.path.join('public', 'glossary.ndtl'), 'w') as f:
    for category in sitedata['glossary']:
        f.write(category.upper() + '\n')

        for term, definition in sitedata['glossary'][category].items():
            f.write('  {} : {}\n'.format(term, definition))

# generate twtxt for peer-to-peer discussion feed
twtxt = website.client.get_collection_view("https://www.notion.so/eidka/51c6a2837c4c4d20b843b936f45ff75b?v=78a7ba17c6da434d8cc61232be5d7064")
with open(os.path.join('public', 'twtxt.txt'), 'w') as f:
    entries = twtxt.collection.get_rows()
    entries = list(map(lambda x: x.get_all_properties(), entries))
    entries = list(sorted(entries, key=lambda x: x['created'], reverse=True))

    for row in entries:         
        #date = row['created'].isoformat()   
        # By default `.isoformat()` returns without timezone stamp
        date = row['created'].strftime('%Y-%m-%dT%H:%M:%S+00:00')
        f.write('{}\t{}\n'.format(date, row['text']))

website.saveCache()

print(sitedata['glossary'])

# print(website.cache)

"""print(website.renderBlock({
    'type': 'numbered_list',
    'children': [
        {'type': 'list_item', 'text': 'test', 'children': [
            {
                'type': 'numbered_list',
                'children': [
                    {'type': 'list_item', 'text': 'test2'},
                    {'type': 'list_item', 'text': 'test3'},
                ]
            }
        ]}
    ]
}))"""