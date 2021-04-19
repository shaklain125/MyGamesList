import aiohttp

import requests

import urllib.parse
from datetime import date, datetime

from ...apis.helper import *

class BaseRawg:
    api_url = 'https://api.rawg.io/api/'

    class Endpoints:
        search = 'games'
        info = 'games/{slug}'
        suggested = 'games/{slug}/suggested'
        stores = 'games/{id}/stores'
        yt_videos = 'games/{id}/youtube'
        screenshots = 'games/{id}/screenshots'

class Rawg(BaseRawg):
    @property
    def session(self):
        session = getattr(self, '_session') if hasattr(self, '_session') else None
        if session is None:
            session = requests.Session()
            setattr(self, '_session', session)
        return session

    def request(self, endpoint, **params):
        try:
            response = self.session.get(self.api_url + endpoint, params=params)
            # print(response.request.url)
            return response.json()
        except Exception as e:
            return {}

    def search(self, keyword, page, page_size = 20):
        endpoint = self.Endpoints.search
        params = self._params(search=keyword, page_size=page_size, page=page)
        params['dates'] = '{century_year}-01-01,{today}'.format(century_year=century_year(),today=str(date.today()))
        params = self._convert_params_utf8(params)

        result = self.request(endpoint, **params)
        r = result['results']
        for i in range(len(result['results'])):
            r[i] = self.get_info(r[i]['slug'], exact=True)
        #     from ...apis.igdb import IGDB
        #     i['igdb'] = IGDB().get_game_by_slug(i['slug'])
        #     if i['igdb']:
        #         if 'cover' in i['igdb']:
        #             i['cover'] = i['igdb']['cover']
        #         if 'storyline' in i['igdb']:
        #             i['storyline'] = i['igdb']['storyline']
        #         if 'summary' in i['igdb']:
        #             i['summary'] = i['igdb']['summary']
        #         if 'platforms' in i['igdb']:
        #             i['platforms'] = i['igdb']['platforms']
        result['results'] = r
        return result

    def _params(self, **extra_params):
        join_arr = lambda arr : (',').join(str(i) for i in arr)
        params = {
            'stores': join_arr([1,2,3,5,6,7,11]),
            'platforms': join_arr([1,4,7,8,11,14,16,18]),
        }
        extra_params = {k: str(v) if not isinstance(v, list) else join_arr(v)  for k,v in extra_params.items()}
        params.update(extra_params)
        return params


    def _convert_params_utf8(self, params):
        return {k: str(v).encode("utf-8") if not isinstance(v, list) else [str(i).encode('utf-8') for i in v] for k,v in params.items()}

    def most_popular(self, count=10):
        print('most_popular')
        endpoint = self.Endpoints.search

        params = self._params(ordering='-added', page_size=count)
        params['dates'] = '{century_year}-01-01,{today}'.format(century_year=century_year(),today=str(date.today()))
        params = self._convert_params_utf8(params)

        result = self.request(endpoint, **params)
        # result['results'].append(self.get_info('dragon-age-2'))
        # for i in result['results']:
        #     from ...apis.igdb import IGDB
        #     i['igdb'] = IGDB().get_game_by_slug(i['slug'])
        return result

    def get_info(self, slug, exact=False, year=None):
        endpoint = self.Endpoints.info
        result = self.request(endpoint.format(slug=slug))
        if 'redirect' in result:
            result = self.request(endpoint.format(slug=result['slug']))
        res = result if 'name' in result else None
        if exact:
            return res
        if res == None:
            rom = self.check_for_roman_numeral(endpoint,slug)
            res = rom['result']
            if year:
                if res == None:
                    y = self.check_for_year_in_slug(endpoint, slug, year)
                    res = y['result']
        if res != None:
            yt = self.request(self.Endpoints.yt_videos.format(id=slug))
            res['youtube_videos'] = yt['results'] if 'results' in yt else []
            s_shots = self.request(self.Endpoints.screenshots.format(id=slug))
            res['screenshots'] = s_shots['results'] if 'results' in s_shots else []
        return res

    def check_for_roman_numeral(self, endpoint, slug):
        s = slug.split('-')
        n_s = []
        for i in s:
            ro = checkIfRomanNumeral(i)
            n_s.append(ro if ro else i)
        s = '-'.join([str(j) for j in n_s])
        result = self.request(endpoint.format(slug=s))
        res = result if 'name' in result else None
        return {'slug':s,'result':res}

    def check_for_year_in_slug(self, endpoint, slug, year):
        original_slug = slug
        slug = '-'.join([slug, year])
        result = self.request(endpoint.format(slug=slug))
        res = result if 'name' in result else None
        if res == None:
            slug = original_slug
            slug = '-'.join([slug, '({0})'.format(year)])
            result = self.request(endpoint.format(slug=slug))
            res = result if 'name' in result else None
        return {'slug':slug,'result':res}

    def stores_of_game(self,id):
        endpoint = self.Endpoints.stores
        result = self.request(endpoint.format(id=id), ordering='store')
        return result


    # def latestgames(self, page=0):
    #     endpoint = self.Endpoints.search
    #     from datetime import date, timedelta
    #     if page == 0:
    #         result = self.request(endpoint,ordering="released", page_size="12",dates=str(date.today() - timedelta(days=30))+ ',' +str(date.today()), platforms='18,4')
    #     else:
    #         result = self.request(endpoint,ordering="released", page=page, page_size="12",dates=str(date.today() - timedelta(days=30))+ ',' +str(date.today()), platforms='18,4')
    #     return result
    #
    # def suggested(self, game, page_size = 5):
    #     endpoint = self.Endpoints.suggested
    #     result = self.request(endpoint.format(slug=self.extract_slug(game)), page_size=page_size)
    #     return result
