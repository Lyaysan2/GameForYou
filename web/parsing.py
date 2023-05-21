import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from collections import Counter
from thefuzz import fuzz
from utils.mychoice import *
from web.models import Game

proc_list = PROCESSOR_CHOICES

graph_list = GRAPHICS_CHOICES

url = 'https://store.steampowered.com/search/?filter=topsellers&page='
pages = 500
games_data = []

replace_proc = {'-': ' ',
                '®': '', '@': '', '™': '', 'series': '', 'cpu': '', 'equivalent': '', 'or better': '',
                'or higher': '', 'or faster': '', 'processor': '', 'physical': '', 'with': '', 'at': '',
                'x64-compible': '', ':': '',
                '/': ',', '|': ',', ' or ': ',', ';': ',',
                }

replace_grap = {'-': ' ',
                '®': '', '@': '', '™': '', 'vram': '', 'with': '', 'or better': '', 'or higher': '', 'or faster': '',
                'or more': '', 'x64-compible': '', 'series': '', 'video card must be': '', 'similar': '', 'super': '',
                'support for pixel shader': '', 'should be': '', 'a directx': '', 'compatible': '', 'a minimum': '',
                'integrated': '', 'graphics': '', 'not': '', 'supported': '', 'equivalent': '', 'at': '', 'least': '',
                'memory': '', 'of': '', ':': '', '3d': '', 'are': '', 'dediced': '', 'model': '', 'shader': '',
                '+': '', 'video': '', 'card': '', 'ram': '', 'capabilities': '', 'opengl': '', 'support': '',
                'any': '', 'type': '', 'directx': '', 'gpu': '', 'gaming': '', 'decided': '', '100%': '',
                '/': ',', '|': ',', ' or ': ',', ';': ',', 'and': ',', '&': ','
                }


def replace_all(text, replace_dict):
    for i, j in replace_dict.items():
        text = text.replace(i, j)
    return text


def convert_to_mb(text):
    match_memory = re.match(r'\W?(\d+)\W?\s?([a-zA-Z]{2,4}).*', text)
    if match_memory is not None:
        if match_memory.group(2) == 'gb' or match_memory.group(2) == 'gigs':
            text = int(match_memory.group(1)) * 1024
        elif match_memory.group(2) == 'mb':
            text = int(match_memory.group(1))
        return text
    else:
        return None


def get_directx(text):
    text = " ".join(text.lower().split())
    match_directs = re.match(r'\w*\s?(\d+.?\d\w?).*', text)
    if match_directs:
        return match_directs.group(1)
    else:
        return None


def replace_with_real_name(game_field, property_list):
    for item in range(len(game_field)):
        similar_property = {}
        for line in property_list:
            similar_property[line] = fuzz.partial_token_sort_ratio(game_field[item], line)
        game_field[item] = Counter(similar_property).most_common(1)[0][0][0]
    game_field = ', '.join(game_field)
    return game_field


def pars_pages():
    for page in range(1, 20):
        print("--------", page)
        r = requests.get(url + str(page))
        soup = BeautifulSoup(r.content, 'html.parser')
        games = soup.select(".search_result_row, .ds_collapse_flag, .app_impression_tracked")

        for game in games:
            release_date = game.find('div', {'class': 'col search_released responsive_secondrow'}).text
            try:
                release_date = datetime.strptime(release_date, '%d %b, %Y')
            except ValueError:
                try:
                    release_date = datetime.strptime(release_date, '%b %Y')
                except ValueError:
                    continue
            if release_date > datetime.now():
                continue
            release_date = release_date.strftime('%Y-%m-%d')

            popularity = game.find('div', {'class': 'col search_reviewscore responsive_secondrow'}).find('span')
            if popularity is not None:
                match_popularity = re.findall(r'(\d{1,3}(,\d{3})*)', str(popularity))
                popularity = match_popularity[1][0]
                popularity = re.sub(',', '', popularity)
            if popularity is not None:
                try:
                    popularity = int(popularity)
                except ValueError:
                    popularity = None

            name = game.find('span', {'class': 'title'}).text

            price = int(re.findall(r'(\d*).*', game.find("div", {"class": "search_price"}).text.strip())[0] or 0)

            link = re.sub('\/\?snr.*', '', game.get("href"))
            r2 = requests.get(link)
            soup2 = BeautifulSoup(r2.content, 'html.parser')

            if soup2.find('div', {'class': 'blockbg'}).text.find('Downloadable Content') != -1:
                continue

            reviews = re.match(r'(.*)', soup2.find('div', {'class': 'summary column'}).text.strip()).group(0)

            try:
                developer = soup2.find('div', {'id': 'developers_list'}).text.strip()
                developer = re.sub(', Inc.', ' Inc', developer)
            except AttributeError:
                continue

            tags = soup2.find('div', {'class': 'glance_tags_ctn popular_tags_ctn'})
            if tags is not None:
                tags = [t.text.strip() for t in tags.findAll('a')]
                tags = ', '.join(tags)

            critics_score = soup2.find('div', {'id': 'game_area_metascore'})
            if critics_score is not None:
                critics_score = re.findall(r'(\d*).*', critics_score.text.strip())[0]
            if critics_score is not None:
                try:
                    critics_score = int(critics_score)
                except ValueError:
                    critics_score = None

            isMinimalReq = True
            sys_req = soup2.find('div', {'class': 'game_area_sys_req_full'})
            if sys_req is None:
                sys_req = soup2.find('div', {'class': 'game_area_sys_req_rightCol'})
                try:
                    sys_req_check = [s for s in sys_req.findAll('li') if s.text.find(':') != -1]
                except AttributeError:
                    continue
                isMinimalReq = False
                if len(sys_req_check) == 0:
                    sys_req = soup2.find('div', {'class': 'game_area_sys_req_leftCol'})
                    isMinimalReq = True
            sys_req = dict(s.text.split(':', 1) for s in sys_req.findAll('li') if s.text.find(':') != -1)

            try:
                os = sys_req['OS']
                list_os = ['XP', 'Vista', '7', '8', '8.1', '10', '11']
                os = re.findall(
                    rf'({list_os[0]}|{list_os[1]}|{list_os[2]}|{list_os[3]}|{list_os[4]}|{list_os[5]}|{list_os[6]})',
                    os)
                for a in range(len(os)):
                    os[a] = f'Windows {os[a]}'
                if 'Windows 7' in os and isMinimalReq:
                    for os_item in range(3, len(list_os)):
                        os.append(f'Windows {list_os[os_item]}')
                os = ', '.join(os)
                if os == '':
                    os = None
            except KeyError:
                os = None

            try:
                processor = sys_req['Processor']
                processor = processor.lower()
                processor = replace_all(processor, replace_proc)
                processor = re.sub(r'\d+\.?\d*\s?ghz', '', processor)
                processor = re.sub(r'\d+\.\d+', '', processor)
                processor = re.sub(r'\([^()]*\)', '', processor)
                processor = re.sub(r'r\d', 'ryzen ', processor)
                processor = processor.split(',')
                processor = [" ".join(p.split()) for p in processor]
                p = 0
                while p < len(processor):
                    match_gen = re.match(r'(.*) (\d)th gen (i\d)', processor[p])
                    if match_gen:
                        processor[p] = f'{match_gen.group(1)} core {match_gen.group(3)} {match_gen.group(2)}400'

                    match_from = re.match(r'(.*) from (.*)', processor[p])
                    if match_from:
                        processor[p] = f'{match_from.group(2)} {match_from.group(1)}'

                    if processor[p].find('intel') == -1 and processor[p].find('dual core') != -1:
                        processor[p] = f'intel {processor[p]}'

                    if processor[p].find('amd') == -1 and processor[p].find('ryzen') != -1:
                        processor[p] = f'amd {processor[p]}'

                    if processor[p].find('intel') == -1 and processor[p].find('quad') != -1:
                        processor[p] = f'intel core 2 quad Q9650'

                    match_i = re.match(r'.*i\d.*', processor[p])
                    if match_i and processor[p].find('intel') == -1:
                        processor[p] = f'intel {match_i.group()}'

                    match_gen_alone = re.match(r'(\d)th gen', processor[p])
                    if match_gen_alone:
                        processor[p - 1] = f'{processor[p - 1]} {match_gen_alone.group(1)}000'
                        del processor[p]
                        continue

                    if processor[p].find('amd') == -1 and processor[p].find('intel') == -1:
                        del processor[p]
                        continue
                    p += 1
                processor = replace_with_real_name(processor, proc_list)
                if processor == '':
                    processor = None
            except KeyError:
                processor = None

            try:
                ram = sys_req['Memory']
                ram = " ".join(ram.lower().split())
                ram = convert_to_mb(ram)
            except KeyError:
                ram = None

            try:
                graphics = sys_req['Graphics']
                graphics = graphics.lower()
                graphics = replace_all(graphics, replace_grap)
                graphics = re.sub(r'\d+\s*(gb|mb)\s*', '', graphics)
                graphics = re.sub(r'\d+\.\d+\w?', '', graphics)
                graphics = re.sub(r'\([^()]*\)', '', graphics)
                graphics = re.sub(r'\d+g', '', graphics)
                graphics = graphics.replace('.', '')
                graphics = graphics.split(',')
                graphics = [" ".join(g.split()) for g in graphics]
                g = 0
                while g < len(graphics):
                    match_gt = re.match(r'(.*)(\d+)gt(.*)', graphics[g])
                    if match_gt:
                        graphics[g] = f'{match_gt.group(1)}{match_gt.group(2)} gt{match_gt.group(3)}'

                    match_vega = re.match(r'(.*)vega(\d+)(.*)', graphics[g])
                    if match_vega:
                        graphics[g] = f'{match_vega.group(1)}vega {match_vega.group(2)}{match_vega.group(3)}'

                    match_hd = re.match(r'(.*)hd(\d+)(.*)', graphics[g])
                    if match_hd:
                        graphics[g] = f'{match_hd.group(1)}hd {match_hd.group(2)}{match_hd.group(3)}'

                    if len(graphics[g].split(' ')) == 1:
                        del graphics[g]
                        continue
                    g += 1
                graphics = replace_with_real_name(graphics, graph_list)
                if graphics == '':
                    graphics = None
            except KeyError:
                graphics = None

            try:
                directx = sys_req['DirectX']
                directx = get_directx(directx)
            except KeyError:
                try:
                    directx = sys_req['DirectX®']
                    directx = get_directx(directx)
                except KeyError:
                    directx = None

            try:
                storage = sys_req['Storage']
                storage = " ".join(storage.lower().split())
                storage = convert_to_mb(storage)
            except KeyError:
                storage = None

            Game.objects.update_or_create(
                link=link, name=name, price=price, release_date=release_date, reviews=reviews,
                popularity=popularity, developer=developer, tags=tags, critics_score=critics_score,
                os=os, processor=processor, ram=ram, graphics=graphics, directx=directx, storage=storage
            )
