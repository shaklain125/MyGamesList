import requests

import urllib.parse
from datetime import date, datetime

import itertools

from django.conf import settings

from ...apis.helper import *

from django.shortcuts import render, redirect, reverse
from gamesrec.models import Game, API
from django.forms.models import model_to_dict

class BaseIGDB:
    api_url = 'https://api-v3.igdb.com/'

    class Endpoints:
        search = 'games/'
        search_count = 'games/count'
        covers = 'covers/'
        release_dates = 'release_dates/'
        companies = 'companies/'
        multiquery = 'multiquery/'
        api_status = 'api_status/'

    def __init__(self):
        self._headers = {
            'Accept': 'application/json',
            'user-key': None
        }

class IGDB(BaseIGDB):

    def __init__(self):
        super(IGDB, self).__init__()
        apis = list(API.objects.all())
        # for i in range(len(apis)):
        #     if self.api_status(apis[i].key)['status'] == False:
        #         apis[i].remove()
        #     else:
        #         break
        self._headers['user-key'] = apis[0].key if len(apis) > 0 else None
        # print(self._headers['user-key'])

    def check_key(self):
        return self._headers['user-key'] != None

    @property
    def session(self):
        session = getattr(self, '_session', None)
        if session is None:
            session = requests.Session()
            setattr(self, '_session', session)
        return session

    def request(self, endpoint, data, **params):
        try:
            # print(data)
            response = self.session.post(self.api_url + endpoint, headers=self._headers, data=data)
            return response.json()
        except Exception as e:
            return {}

    def _multiple_or_q(self, q, vals):
        rq = ''
        for i in range(len(vals)):
            if i == 0:
                rq = '{0} = {1}'.format(q,vals[i])
            else:
                rq = '{0} | {1} = {2}'.format(rq,q,vals[i])
        return '({0})'.format(rq)
                                        #xbox     #ps           #nintendo      #wii     #VR
    def _platform_q(self, main=[6], p1=[12,49] +[9,48] + [20,37,130,137,160] + [5] + [162,165]): #6=pc 9=ps3 12=x360 48=ps4 49=xone 130=nswitch
        q = 'platforms'
        pq = '{0} = {1}'.format(q, str((main + p1)))
        for i in range(len(p1)):
            pq = '{0} | {1} = {2}'.format(pq, q, str(main+[p1[i]]))
        return '({0})'.format(pq)

    def _wsite_categ_q(self, default=True, find_games_of_sites = [13,16,17,2,3,1]):
        not_null = self._multiple_or_q('websites.category',find_games_of_sites)
        if not default:
            return '((websites = null) | {0})'.format(not_null)
        return not_null

    def _filter_out_games_only(self, only=[0,4]): #2, 3 excluded
        return self._multiple_or_q('category',only)

    def _gquery1(self, wsite_categs=None, wsite_default=True, platforms=None, filter_out_games=None, released_only=True, filters=None, sort=None):
        if sort != None and 'created_at' in sort:
            wsite_categs = self._wsite_categ_q(wsite_default) if wsite_categs == None else wsite_categs
            platforms = '(platforms = (6,12,49,9,48,20,37,130,137,160,5,162,165,20,38,46))'
            # platforms = self._platform_q() if platforms == None else 'platforms = ' + platforms
            filter_out_games = self._filter_out_games_only() if filter_out_games == None else filter_out_games
            main_g = 'name !~ *"edition"*' #+ '& version_parent = null'
            released_only = 'created_at <= {today} & '.format(today=str(int(datetime.strptime(str(date.today()),'%Y-%m-%d').timestamp()))) if released_only else ''
            req = [wsite_categs, platforms, filter_out_games,main_g]
            req.append(filters) if filters else None
            rels = 'created_at != null & {released_only}created_at >= {cent_d}'.format(released_only=released_only,cent_d=year_dt(1980,epoch=True))
            if sort != None:
                rels = '{0} {1}'.format(rels, sort)
            return {
                'req' : f"(({' & '.join(req[0:2])}) | (websites.url ~ *\"steam\"*)) & ({' & '.join(req[2:])})",
                'released_only': rels
            }
        else:
            # wsite_categs = self._wsite_categ_q(wsite_default) if wsite_categs == None else wsite_categs
            # platforms = '(platforms = (6,12,49,9,48,20,37,130,137,160,5,162,165,20,38,46))'
            # # platforms = self._platform_q() if platforms == None else 'platforms = ' + platforms
            # filter_out_games = self._filter_out_games_only() if filter_out_games == None else filter_out_games
            # main_g = 'name !~ *"edition"*' #+ '& version_parent = null'
            # released_only = '(first_release_date = null| first_release_date <= {today}) & '.format(today=str(int(datetime.strptime(str(date.today()),'%Y-%m-%d').timestamp()))) if released_only else ''
            # req = [wsite_categs, platforms, filter_out_games,main_g]
            # req.append(filters) if filters else None
            # rels = '(first_release_date = null| (first_release_date != null & {released_only}first_release_date >= {cent_d}))'.format(released_only=released_only,cent_d=year_dt(1980,epoch=True))
            # if sort != None:
            #     rels = '{0} {1}'.format(rels, sort)
            # return {
            #     'req' : f"(({' & '.join(req[0:2])}) | (websites.url ~ *\"steam\"*)) & ({' & '.join(req[2:])})",
            #     'released_only': rels
            # }
            wsite_categs = self._wsite_categ_q(wsite_default) if wsite_categs == None else wsite_categs
            platforms = '(platforms = (6,12,49,9,48,20,37,130,137,160,5,162,165,20,38,46))'
            # platforms = self._platform_q() if platforms == None else 'platforms = ' + platforms
            filter_out_games = self._filter_out_games_only() if filter_out_games == None else filter_out_games
            main_g = 'name !~ *"edition"*' #+ '& version_parent = null'
            released_only = 'first_release_date <= {today} & '.format(today=str(int(datetime.strptime(str(date.today()),'%Y-%m-%d').timestamp()))) if released_only else ''
            req = [wsite_categs, platforms, filter_out_games,main_g]
            req.append(filters) if filters else None
            rels = '((websites.url ~ *"steam"*) | first_release_date != null & {released_only}first_release_date >= {cent_d})'.format(released_only=released_only,cent_d=year_dt(1980,epoch=True))
            if sort != None:
                rels = '{0} {1}'.format(rels, sort)
            return {
                'req' : f"(({' & '.join(req[0:2])}) | (websites.url ~ *\"steam\"*)) & ({' & '.join(req[2:])})",
                'released_only': rels
            }

    def multiquery(self, endpoint, name, query):
        q = """
        query {endpoint} "{name}" {{
            {query}
        }};
        """
        return q.format(endpoint=endpoint,name=name,query=query)

    def search_by_weblink(self, links):
        # print('search by weblink')

        # print(links['steam'])
        # print(links['gog'])
        # print(links['epic'])

        endpoint = self.Endpoints.search
        url = None
        url2 = None
        wsite = -1

        if links['steam'] != None:
            wsite = 13
            url = links['steam']
            url = (url[url.index('store.'):]).rstrip('/')
            url2 = url[:url.rfind('/')] + '/'
            if url2.endswith('app/'):
                url2 = None
            else:
                url2 = url2.rstrip('/')
        else:
            if links['gog'] != None:
                wsite = 17
                url = links['gog']
                url = (url[url.index('gog.'):]).rstrip('/')
            else:
                if links['epic'] != None:
                    wsite = 16
                    url = links['epic']
                    url = (url[url.index('/product/'):]).rstrip('/')
                    url = url[:url.rfind('/')]
                else:
                    return None
        # print(url)
        if url2 != None:
            url2 = """ | websites.url ~ *"{0}"*""".format(url2)
        else:
            url2 = ''
        gq = self._gquery1(wsite_categs=self._wsite_categ_q([wsite]))
        data = """
        fields *,cover.*,websites.*;
        where (websites.url ~ *"{0}"* {1}) & {2} & {3};
        limit 1;
        """
        data = data.format(url, url2, gq['req'], gq['released_only'])
        result = self.request(endpoint, data=data)
        return result

    def latestgames(self, limit=12):
        print('latest games')
        endpoint = self.Endpoints.search
        gq = self._gquery1()
        data = """
        fields *,cover.*,websites.*;
        where {0} & {1};
        limit """+str(limit)+""";
        sort first_release_date desc;
        """
        data = data.format(gq['req'], gq['released_only'])
        result = self.request(endpoint, data=data)
        for i in result:
            if 'cover' in i:
                i['cover']['url'] = 'https:' + i['cover']['url']
            if len(Game.objects.filter(id=i['id'])) > 0:
                i['url'] = Game.objects.filter(id=i['id'])[0].url
            else:
                i['url'] = '#'
            # from ...apis.rawg import Rawg
            # i['rawg'] = Rawg().get_info(i['slug'])
        return result


    def _req_fields(self,q=None, more=None, rec=False):
        f = ['*', 'cover.*', 'websites.*',
            'platforms.*', 'platforms.platform_logo.*',
            'age_ratings.*', 'age_ratings.content_descriptions.*',
            'involved_companies.*', 'involved_companies.company.*, involved_companies.company.websites.*', 'involved_companies.company.developed.id', 'involved_companies.company.published.id',
            'game_modes.*', 'player_perspectives.*', 'genres.*', 'themes.*',
            'videos.*', 'screenshots.*', 'artworks.*',
            'collection.*', 'collection.games.*',
            # 'bundles.*', 'dlcs.*', 'expansions.*',
            # 'game_engines.*','game_engines.companies.*','game_engines.companies.websites.*',
            'external_games.*',#'similar_games.id','similar_games.*',
            'release_dates.*','alternative_names.*',
            # 'keywords.*',
            'multiplayer_modes.*',
            'franchise.*','franchises.*'
            ]
        if more != None:
            f += more
        if not rec:
            coll = self._req_fields(q='collection.games', more=more, rec=True)
            return '{fields} {values}'.format(fields='fields',values=', '.join(f+coll))
        else:
            if q:
                # o_f = f
                # del o_f[o_f.index('similar_games.*')]
                # f = o_f
                f = ['*', 'websites.*','platforms.*']
                if more != None:
                    f += more
                f = ['{0}.{1}'.format(q,i) for i in f]
                # if q == 'collection.games':
                #     similar_games = self._req_fields(q='similar_games', more=more, rec=True)
                #     return similar_games + f
                # elif q == 'similar_games':
                #     f = o_f
                #     if more != None:
                #         f += more
                #     f = ['{0}.{1}'.format(q,i) for i in f]
                return f
            else:
                return '{fields} {values}'.format(fields='fields',values=', '.join(f))

    def search2(self, keyword, page=1, released_only=False,filters=None, sort=None, fields=None, size=20):
        keyword,offset = keyword.rstrip().lstrip(), size * (int(page)-1)


        endpoint = self.Endpoints.multiquery

        gq = self._gquery1(released_only=released_only, filters=filters, sort=sort)
        req_fields = self._req_fields() if not fields else fields
        where1, where2 = gq['req'], gq['released_only']

        method = 2 # methods 1 and 2 : 1 is for searching only once even if count is 0, 2 is for keep searching after count = 0

        data = """
        {fields};
        where (name ~ *"{keyword}"* | alternative_names.name ~ *"{keyword}"*) & {where1} & {where2};
        offset {offset};
        limit """+str(size)+""";
        """

        def qu(i,k, count=False, fields=req_fields):
            return self.multiquery(endpoint=self.Endpoints.search if not count else self.Endpoints.search_count,name='search_query{count}{i}'.format(i=i,count=('_count'if count else '')),query=q1.format(keyword=k, fields=fields))

        def qu_e(i,count=False, fields=req_fields):
            return self.multiquery(endpoint=self.Endpoints.search if not count else self.Endpoints.search_count,name='search_query{count}{i}'.format(i=i,count=('_count'if count else '')),query=q1.format(fields=fields))

        def meth(i, k, m_queries):
            count_q = qu(i=i, k=k, count=True, fields='fields id')
            return '{0} {1} {2}'.format(m_queries, count_q, qu(i=i,k=k) if method == 1 else '')

        def not_found():
            # print('No results found')
            r = {
                'result' : [],
                'total_pages': 0,
                'page' : int(page),
                'keyword': keyword,
                'count': count,
                'offset':offset
            }
            return r

        def num_of_pages(count):
            import math
            num_of_pages = 0
            if count != 0:
                if count > (5000 + size):
                    count = (5000 + size)
                num_of_pages = count/size
                if num_of_pages < 1 and num_of_pages > 0:
                    num_of_pages = 1
                else:
                    m = math.modf((count/size))
                    num_of_pages = int(m[1]) + 1
                    if m[0] == 0:
                        num_of_pages -=1
                # if count == 5020:
                #     num_of_pages -= 1
            return num_of_pages

        q1 = data.format(keyword='{keyword}',offset=offset,fields='{fields}',where1=where1, where2=where2)
        k,i,m_queries,count = keyword,1,'',0
        result = None
        # keyword = k = 'sdvsdvsvsdv'
        if len(k) == 0:
            data_e = """
            {fields};
            where {where1} & {where2};
            offset {offset};
            limit """+str(size)+""";
            """
            q1 = data_e.format(offset=offset,fields='{fields}',where1=where1, where2=where2)
            count_q = qu_e(i=i, count=True, fields='fields id')
            m_queries = count_q + qu_e(i=i)
            method=1
        else:
            while len(k) > 0 and i < (2 if method == 1 else 6):
                m_queries = meth(i=i, k=k, m_queries=m_queries)
                k = k[:len(k)-1]
                i = i+1
        # print(m_queries)
        result = self.request(endpoint, data=m_queries)
        if method == 1:
            count = result[0]['count'] if len(result) > 0 and 'count' in result[0] else []
            result = result[1]['result'] if len(result) > 1 and 'result' in result[1] else []
        else:
            c, m_query = 0, ''
            for i in range(len(result)):
                # print(result)
                if 'count' in result[i]:
                    if result[i]['count'] > c:
                        count = result[i]['count']
                        search_q = qu(i=i+1,k=keyword[:len(keyword)-i])
                        m_query = search_q
                        break
            if len(m_query) == 0:
                return not_found()
            # print(m_query)
            result = self.request(endpoint, data=m_query)
            result = result[0]['result'] if len(result) > 0 and 'result' in result[0] else []

        if len(result) > 0:
            for i in result:
                if 'name' in i:
                    title_sim = similar(keyword.lower(),i['name'].lower())
                    i['name_similarity'] = title_sim
                else:
                    i['name_similarity'] = 0
                if len(Game.objects.filter(id=i['id'])) > 0:
                    i['url'] = Game.objects.filter(id=i['id'])[0].url
                else:
                    i['url'] = '#'
            if (filters == None) or (sort == None):
                result = sorted(result, key = lambda i: i['name_similarity'], reverse=True)
            r = {
                'result' : result,
                'total_pages': num_of_pages(count),
                'page' : int(page),
                'keyword': keyword,
                'count': count,
                'offset':offset
            }
            return r
        else:
            return not_found()

    def search_count2(self, q):
        endpoint = self.Endpoints.search_count
        c1 = self.request(endpoint, data=q)
        if 'count' in c1:
            c = c1['count']
            return c
        else:
            return 0

    #'fields name, first_release_date,cover.*, summary, storyline'
    def get_game_by_id(self, id, fields=None, collection=True, gm=None):
        endpoint = self.Endpoints.multiquery
        gq = self._gquery1(released_only=False,wsite_default=False)
        req_fields= self._req_fields() if not fields else fields
        req, released=gq['req'], gq['released_only']
        data = """
        {fields};
        where id={id} & {req} & {released};
        """
        data1 = data.format(id=id, fields=req_fields, req=req, released=released)
        def qu(name=None, q=None):
            nonlocal q_count
            q_count+=1
            return self.multiquery(endpoint=self.Endpoints.search,name='{name}{i}'.format(i=q_count, name=name + '_' if name else 'game_'),query=(q if q else data1))
        def get_collection():
            d = """
            {fields};
            where collection.games=[{id}] & id != {id} & {req} & {released};
            sort first_release_date desc;
            """
            return qu(name='game_collection',q=d.format(id=id, fields=req_fields, req=req,released=released))
        q_count = 0
        m_queries = qu()
        if collection:
            m_queries += get_collection()
        # print(m_queries)
        result = self.request(endpoint=endpoint, data=m_queries)
        res = {}
        if len(result) > 0:
            res = result[0]['result']
            if len(res) > 0:
                res = res[0]
                res['url'] = gm.url if gm != None else '#'
                res['first_release_date'] = gm.first_release_date if gm != None else None
                res['steam'] = get_steam(res)
                # res['screenshots'] = [{'id':s.pk, 'url':f'https://images.igdb.com/igdb/image/upload/t_thumb/{s.image_id}.jpg'} for s in gm.screenshot_set.all()] if gm != None else []
                if collection:
                    res['game_collection'] = result[1]['result']
                return res
        return None

    def get_game_by_slug(self, slug, fields=None, mquery_only=False):
        endpoint = self.Endpoints.multiquery
        gq = self._gquery1(released_only=False,wsite_default=False)
        req_fields = self._req_fields() if not fields else fields
        req, released=gq['req'], gq['released_only']
        data = """
        {fields};
        where slug="{slug}" & {req} & {released};
        """
        data1 = data.format(slug='{slug}', fields=req_fields, req=req,released=released)

        def qu(s, name=None, q=None):
            nonlocal q_count
            q_count+=1
            return self.multiquery(endpoint=self.Endpoints.search,name='{name}{i}'.format(i=q_count, name=name + '_' if name else 'game_'),query=(q if q else data1.format(slug=s)))

        def int_rom_chk_query():
            s = slug.split('-')
            n_s = []
            for i in s:
                ro = intToRoman(i)
                n_s.append(ro if ro else i)
            s = '-'.join([str(j) for j in n_s])
            return qu(s=s,name='int_rom_chk')

        def get_collection():
            d = """
            {fields};
            where collection.games.slug="{slug}" & slug != "{slug}" & {req} & {released};
            sort first_release_date desc;
            """
            return qu(s=slug,name='game_collection',q=d.format(slug=slug, fields=req_fields, req=req,released=released))

        q_count = 0
        sl,m_queries = slug,''
        while sl.rfind('-') != -1:
            m_queries += qu(s=sl)
            sl = sl[:sl.rfind('-')]
        else:
            m_queries += qu(s=sl)

        m_queries += int_rom_chk_query()

        if mquery_only:
            return m_queries

        # print(q_count)
        coll = False
        if q_count < 10:
            m_queries += get_collection()
            coll = True

        # print(m_queries)

        result = self.request(endpoint=endpoint, data=m_queries)

        if not coll:
            result.append(self.request(endpoint=endpoint, data=get_collection())[0])

        c = 0
        for i in result:
            l = len(i['result'])
            if l > c:
                c = l
                game_coll = result[q_count-1]['result']
                result = i['result'][0]
                if len(Game.objects.filter(id=result['id'])) > 0:
                    result['url'] = Game.objects.filter(id=result['id'])[0].url
                else:
                    result['url'] = '#'
                result['game_collection'] = game_coll
                break
        return result if c > 0 else None

    def get_collection(self,slug):
        endpoint = self.Endpoints.search
        gq = self._gquery1(released_only=False,wsite_default=False)
        req_fields= self._req_fields()
        data = """
        {fields};
        where collection.games.slug="{slug}" & slug != "{slug}" & {req} & {released};
        """
        data1 = data.format(slug=slug, fields=req_fields, req=gq['req'], released=gq['released_only'])
        # print(data1)
        result = self.request(endpoint, data=data1)
        return result

    def get_genres_and_themes(self):
        genres = self.multiquery('genres/','genres','fields name; limit 100;sort name asc;')
        themes = self.multiquery('themes/','themes','fields name; limit 100;sort name asc;')
        mquery = genres + themes
        result = self.request(endpoint=self.Endpoints.multiquery, data=mquery)
        res = {}
        res['genres'] = result[0]['result']
        res['themes'] = result[1]['result']
        return res

    def get_multi_games_by_id(self, ids, fields, id_as_key=False):
        endpoint = self.Endpoints.multiquery

        gq = self._gquery1(released_only=False)
        req_fields = self._req_fields() if not fields else fields
        where1, where2 = gq['req'], gq['released_only']

        m_queries = []

        data_e = """
        {fields};
        where id={id};
        """
        q1 = data_e.format(id='{id}',fields=req_fields)

        def qu(i, id):
            return self.multiquery(endpoint=self.Endpoints.search,name='game{i}'.format(i=i),query=q1.format(id=id))

        n_req = 1
        if len(ids) > 10:
            import math
            n_req = int(math.modf(len(ids)/10)[1])
            if (len(ids) % 10) != 0:
                n_req+=1
        reqs = []
        for p in range(1, len(ids)+1):
            q = qu(i=p,id=ids[p-1])
            if len(m_queries) == 10 or p == len(ids):
                if p == len(ids):
                    m_queries.append(q)
                reqs.append('\n'.join(m_queries))
                m_queries = []
                m_queries.append(q)
            else:
                m_queries.append(q)
        results = []
        r_dict = {}
        for r in reqs:
            result = self.request(self.Endpoints.multiquery, data=r)
            if len(result) >= 1:
                for g in result:
                    r_dict[g['result'][0]['id']] = g['result'][0]
            result = [g['result'][0] for g in result] if len(result) >= 1 else []
            if len(results) == 0:
                results = result
            else:
                results += result
        return results if not id_as_key else r_dict

    def get_multi_games_by_id2(self, ids, fields, id_as_key=False):
        endpoint = self.Endpoints.multiquery

        gq = self._gquery1(released_only=False)
        req_fields = self._req_fields() if not fields else fields
        where1, where2 = gq['req'], gq['released_only']

        m_queries = []

        data_e = """
        {fields};
        where id={id};
        """
        q1 = data_e.format(id='{id}',fields=req_fields)

        def qu(i, id):
            return self.multiquery(endpoint=self.Endpoints.search,name='game{i}'.format(i=i),query=q1.format(id=id))

        reqs = []
        limit = 10
        limit = limit if len(ids) >= limit else (1 if len(ids) > 0 else 0)
        import sys
        for p in range(0, len(ids), 10):
            # sys.stdout.write(f'\r{p} {[str(id) for id in ids[p:(p)+limit]]} {p+limit} {len(ids)} ')
            # sys.stdout.write("\033[K")
            q = qu(i=p+1,id=f"({','.join([str(id) for id in ids[p:(p)+limit]])})")
            if len(m_queries) == 10:
                reqs.append('\n'.join(m_queries))
                m_queries = []
            m_queries.append(q)
            if (p+limit) >= len(ids):
                reqs.append('\n'.join(m_queries))
        results = []
        r_dict = {}
        req_count = 0

        # print(len(reqs))

        for r in reqs:
            result = self.request(self.Endpoints.multiquery, data=r)
            if len(result) >= 1:
                for g in result:
                    for res1 in g['result']:
                        r_dict[res1['id']] = res1
            if len(result) >= 1:
                rl = []
                for g in result:
                    rl += g['result']
                result = rl
            else:
                result = []
            if len(results) == 0:
                results = result
            else:
                results += result
            req_count += 1
            sameln(f'{req_count}/{len(reqs)}  ->  {len(results)}')
        return results if not id_as_key else r_dict

    def get_mult_queries(self,pages,released_only=False,filters=None, sort=None, fields=None, size=20):
        endpoint = self.Endpoints.multiquery

        gq = self._gquery1(released_only=released_only, filters=filters, sort=sort)
        req_fields = self._req_fields() if not fields else fields
        where1, where2 = gq['req'], gq['released_only']

        m_queries = []

        data_e = """
        {fields};
        where {where1} & {where2};
        offset {offset};
        limit """+str(size)+""";
        """
        # sort rating_count desc;
        q1 = data_e.format(offset='{offset}',fields=req_fields,where1=where1, where2=where2)

        def qu(i, offset):
            return self.multiquery(endpoint=self.Endpoints.search,name='search_query{i}'.format(i=i),query=q1.format(offset=offset))

        n_req = 1
        if pages > 10:
            import math
            n_req = int(math.modf(pages/10)[1])
            if (pages % 10) != 0:
                n_req+=1
        # print(pages, n_req)
        reqs = []
        for p in range(1,pages+1):
            offset = size * (int(p)-1)
            q = qu(i=p,offset=offset)

            # if len(m_queries)+1 == 10 or p == (pages):
            #     if p == (pages):
            #         m_queries.append(q)
            #     # print(int(p),'Q:',len(m_queries))
            #     reqs.append('\n'.join(m_queries))
            #     m_queries = []
            #     m_queries.append(q)
            # else:
            #     m_queries.append(q)

            if len(m_queries)+1 == 10: #IMPORTANT CHECKING IF WORKS
                reqs.append('\n'.join(m_queries))
                m_queries = []
            m_queries.append(q)
            if p == (pages):
                reqs.append('\n'.join(m_queries))


        # print('reqs len',len(reqs))

        results = []
        for r in reqs:
            # print(r)
            result = self.request(self.Endpoints.multiquery, data=r)
            result_arr = []
            def get_p_result(r_val):
                nonlocal result_arr,r
                result_arr+=r_val
            [get_p_result(g['result']) if 'result' in g else None for g in result] if len(result) >= 1 else None#result[1]['result'] if len(result) > 1 and 'result' in result[1] else []
            result = result_arr
            if len(results) == 0:
                results = result
            else:
                results += result
        return results

    def api_status(self, key=None):
        h = self._headers.copy()
        if key != None and len(key.strip()) != 0:
            h['user-key'] = key
        p = self.session.get(self.api_url + self.Endpoints.api_status, headers=h)
        r = {'status':p.status_code == 200, 'json':p.json()}
        return r


    # def search_rec(self, keyword, length=None, offset=0, once=False, search_op=True):
    #     endpoint = self.Endpoints.search
    #     gq = self._gquery1()
    #     data = ''
    #     if search_op:
    #         data = """
    #         search "{keyword}";
    #         {fields};
    #         where {where1} & {where2};
    #         offset {offset};
    #         limit 20;
    #         """
    #     else:
    #         data = """
    #         {fields};
    #         where name ~ *"{keyword}"* & {where1} & {where2};
    #         offset {offset};
    #         limit 20;
    #         """
    #     q = keyword if length == None else keyword[:length]
    #     if length != None and keyword[:length-1] == q.rstrip():
    #         q = q.rstrip()
    #         q = q[:len(q)]
    #         length = len(q)
    #     print('search_rec -> "{k}" -> search_op={s_op} -> offset={offset}'.format(k=str(q), s_op=search_op, offset=offset))
    #     data1 = data.format(offset=offset, fields=self._req_fields(),keyword=q,where1=gq['req'], where2=gq['released_only'])
    #     q1 = data.format(offset=0, fields=self._req_fields(),keyword=q,where1=gq['req'], where2=gq['released_only'])
    #     result = self.request(endpoint, data=data1)
    #     if length == None:
    #         length = len(keyword)
    #     if (len(result) != 0 or  length <= 2) or once:
    #         if len(result) != 0:
    #             for i in result:
    #                 title_sim = similar(keyword.lower(),i['name'].lower())
    #                 i['name_similarity'] = title_sim
    #                 i['game_id']= i['id']
    #         return {'result':result, 'q':q1, 'q_k': q}
    #     else:
    #         return self.search_rec(keyword=keyword,length=length-1, offset=offset, once=once, search_op=search_op)
    #
    # def search(self, keyword, offset=0, page=1, rec=False):
    #     check_zeroOffset = None
    #     s_count = 0
    #     num_of_pages = 0
    #     c_same = 0
    #     if not rec:
    #         import math
    #         check_zeroOffset = self.search(keyword=keyword, rec=True)
    #         c_count = check_zeroOffset['count']
    #         s_count = c_count['c']
    #         count = c_count['c']
    #         num_of_pages = count/20
    #         if num_of_pages < 1 and num_of_pages > 0:
    #             num_of_pages = 1
    #         else:
    #             num_of_pages = int(math.modf((count/20))[1]) + 1
    #         # print(' n page = ' + str(num_of_pages))
    #         # print(s_count)
    #
    #         if int(page) > num_of_pages:
    #             return None
    #         else:
    #             curr = int(math.modf(((len(check_zeroOffset['result']))/20))[1])+1
    #             print('curr ' + str(curr))
    #             if int(page) == 1:
    #                 check_zeroOffset['result'] = check_zeroOffset['result'][(20 * (int(page)-1)):]
    #                 check_zeroOffset['result'] = check_zeroOffset['result'][:20]
    #                 check_zeroOffset['count'] = s_count
    #                 check_zeroOffset['total_pages'] =num_of_pages
    #                 return check_zeroOffset
    #
    #     if len(keyword) != 0:
    #         from collections import defaultdict
    #
    #         res1 = self.search_rec(keyword=keyword if rec else check_zeroOffset['q1']['k'],offset=offset, once=True if not rec else False)
    #         q1 = self.encryption_q(res1['q'], encrypt=True)
    #         q1_k = res1['q_k']
    #         res1 = res1['result']
    #         # print('res1 ' + str(len(res1)))
    #
    #         res2 = self.search_rec(keyword=keyword if rec else check_zeroOffset['q2']['k'],offset=offset, once=True if not rec else False, search_op=False)
    #         q2 = self.encryption_q(res2['q'], encrypt=True)
    #         q2_k = res2['q_k']
    #         res2 = res2['result']
    #         # print('res2 ' + str(len(res2)))
    #
    #         count_same = count_same_items(res1,res2)
    #         m_count = len(res1+res2)-count_same
    #         keys_merged_count = m_count
    #
    #         # print('count_same ' + str(count_same))
    #         # print('merged_count ' + str(m_count))
    #
    #         m = merge('game_id',res1,res2)
    #
    #         res1 = [m[i] for i in m.keys()]
    #
    #         res1 = sorted(res1, key = lambda i: i['name_similarity'], reverse=True)
    #
    #         return {
    #             'result':res1,
    #             'keys_merged_count' : keys_merged_count,
    #             'q1': {'q':q1, 'k':q1_k},
    #             'q2': {'q':q2,'k':q2_k},
    #             'total_pages': num_of_pages,
    #             'count_same': count_same,
    #             'count':self.search_count(keyword,{'q':q1},{'q':q2},count_same) if rec else s_count
    #             }
    #     else:
    #         print('len of keyword equals 0')
    #         endpoint = self.Endpoints.search
    #         gq = self._gquery1()
    #         data = """
    #         {fields};
    #         where {where1} & {where2};
    #         offset {offset};
    #         limit 20;
    #         """
    #         data1 = data.format(offset=offset,fields=self._req_fields(),where1=gq['req'], where2=gq['released_only'])
    #         q1 = data.format(offset=0,fields=self._req_fields(),where1=gq['req'], where2=gq['released_only'])
    #         result = self.request(endpoint, data=data1)
    #         q1 = self.encryption_q(q1, encrypt=True)
    #         return {
    #             'result':result,
    #             'q1': {'q':q1,'k':keyword},
    #             'total_pages': num_of_pages,
    #             'count':self.search_count(keyword,{'q':q1}) if rec else s_count
    #             }
    #
    # def search_count(self, keyword, q1=None, q2=None, count_same=0):
    #     c = 0
    #     endpoint = self.Endpoints.search_count
    #     q1 = self.encryption_q(q1['q'], encrypt=False)
    #     c1 = self.request(endpoint, data=q1)
    #     if 'count' in c1:
    #         c = c1['count']
    #         print('c1 ' + str(c))
    #     if len(keyword) == 0:
    #         return {'c':c}
    #     else:
    #         q2 = self.encryption_q(q2['q'], False)
    #         c2 = self.request(endpoint, data=q2)
    #         if 'count' in c2:
    #             c2 = c2['count']
    #             print('c2 ' + str(c2))
    #             c += c2
    #             c = c-count_same
    #         print('count_same ' + str(count_same))
    #         print('c ' + str(c))
    #         return {'c':c, 'original': c+count_same}
    #
    # def encryption_q(self, q, encrypt, get_bytes=False):
    #     from cryptography.fernet import Fernet
    #     key = b'H_Vnv-Roe3ESJjFlZAOikapWt1oAQYEn_XGlHB4jasI='
    #     f = Fernet(key)
    #     if encrypt:
    #         encoded = f.encrypt(q.encode())
    #         if get_bytes:
    #             return encoded
    #         return encoded.decode('utf8').replace("'", '"')
    #     else:
    #         encrypted_q = q.encode()
    #         decrypted = f.decrypt(encrypted_q)
    #         return decrypted.decode()
