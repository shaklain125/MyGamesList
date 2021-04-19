from gamesrec.apis.igdb import IGDB
from gamesrec.apis.rawg import Rawg
from gamesrec.models import *
from gamesrec.apis.helper import *
from django.contrib.staticfiles.templatetags.staticfiles import static
from datetime import datetime, date, timedelta
import pytz
from bs4 import BeautifulSoup
import requests
import sys

class GamesUpdateMgr:

    def __init__(self):
        self.fields = 'fields websites.*,created_at, id, slug, name, rating, rating_count, first_release_date, popularity, cover.url, genres.*, player_perspectives.*, themes.*, game_modes.*, platforms.*, alternative_names.*, summary, storyline,age_ratings.*,artworks.*,screenshots.*'


    def steam_released_date(self, link):
        try:
            # b = BeautifulSoup(requests.get(link).content, 'html.parser').select_one('.release_date .date').get_text()
            # int(str(int(datetime.strptime(b,'%d %b, %Y').timestamp())))
            id = None
            for i in link.split('/'):
                try:
                    id = int(i)
                except Exception as e:
                    pass
            if id == None:
                return None
            d = requests.get(f'https://store.steampowered.com/api/appdetails/?appids={id}').json()
            d = d[str(id)]['data']['release_date']['date']
            # print(d)
            return int(str(int(datetime.strptime(d,'%d %b, %Y').timestamp())))
        except Exception as e:
            return None

    def extra_ctx(self, g_d):
        e = {
            'genres': g_d['genres'] if 'genres' in g_d else None,
            'perspectives': g_d['player_perspectives'] if 'player_perspectives' in g_d else None,
            'themes': g_d['themes'] if 'themes' in g_d else None,
            'game_modes': g_d['game_modes'] if 'game_modes' in g_d else None,
            'platforms': g_d['platforms'] if 'platforms' in g_d else None,
            'alternative_names': g_d['alternative_names'] if 'alternative_names' in g_d else None,
            'age_ratings': g_d['age_ratings'] if 'age_ratings' in g_d else None,
            'artworks': g_d['artworks'] if 'artworks' in g_d else None,
            'screenshots': g_d['screenshots'] if 'screenshots' in g_d else None,
            'websites': g_d['websites'] if 'websites' in g_d else None,
        }
        [g_d.pop(i,None) for i in ['genres','player_perspectives','themes','game_modes','platforms','alternative_names','age_ratings', 'artworks','screenshots','websites','created_at']]
        return {'g_d':g_d, 'e':e}

    def add_latest_only_if_not_exists_or_update_them(self, option='add'):
        igdb = IGDB()
        rawg = Rawg()
        games = []
        filters = ['platforms!=[6]','platforms=[6]']
        total_count = 0
        total_count_fin = igdb.search2(keyword='',fields='fields id')
        total_count_fin = total_count_fin['count'] if 'count' in total_count_fin else 0
        db_count = Game.objects.all().count()
        gs = igdb.search2(keyword='',fields=self.fields,
                                    sort=f'; sort updated_at desc', size=500) #& first_release_date <= {str(int(datetime.now().timestamp()))};
        gs = gs['result']
        count = len(gs)
        total_count+= count
        print(f'{count}/{total_count_fin}')
        updated = 1
        for g in range(count):
            g_d = self.get_rawg_game_details(gs[g],rawg)
            if g_d == None:
                continue

            _extra = self.extra_ctx(g_d)
            g_d = _extra['g_d']
            _extra = _extra['e']

            [g_d.pop(i,None) for i in ['name_similarity','url']]

            def add_only():
                nonlocal g_d, _extra, updated
                # print(len(Game.objects.filter(id=g_d['id'])), g_d['id'], db_count, total_count_fin)
                if (not Game.objects.filter(id=g_d['id']).exists()) and db_count != total_count_fin:
                    #ADD HERE
                    g_obj = Game(**g_d)
                    print('NEW', g_d['slug'])
                    g_obj._extra = _extra
                    g_obj.save()

            def update_only():
                nonlocal g_d, _extra, updated
                if Game.objects.filter(id=g_d['id']).exists():
                    g_obj = Game(**g_d)
                    print(f'{updated}/{count}','UPDATE', g_d['slug'])
                    [g_d.pop(i,None) for i in ['id','slug']]
                    g_obj._extra = _extra
                    g_obj.save(update_fields=g_d)
                    updated+=1

            if option == 'add':
                add_only()
            elif option == 'update':
                update_only()
            elif option == 'add_update':
                if Game.objects.filter(id=g_d['id']).exists():
                    g_obj = Game(**g_d)
                    # print(f'{updated}/{count}','UPDATE', g_d['slug'])
                    [g_d.pop(i,None) for i in ['id','slug']]
                    g_obj._extra = _extra
                    g_obj.save(update_fields=g_d)
                    updated+=1
                else:
                    if db_count != total_count_fin:
                        #ADD HERE
                        g_obj = Game(**g_d)
                        print('NEW', g_d['slug'])
                        g_obj._extra = _extra
                        g_obj.save()

        if option == 'add' or option == 'add_update':
            if db_count == total_count_fin:
                print('No new games to add')
            if option == 'add_update':
                print(f'{updated-1}/{count}','UPDATED')
        print('total_count',total_count_fin, 'db_count',Game.objects.all().count())

    def add_all_if_not_exists_or_update_all(self, option='add', log=True):
        if log:
            print('***********************************BEGIN********************************************\n')
            print(f'[{str(datetime.now())}]\n')
        igdb = IGDB()
        rawg = Rawg()
        games = []
        d1 = str(int((datetime.now()+timedelta(days=10*365)).timestamp()))#str_dt_timestamp('2016-11-27')#
        d2 = str(int((epoch_to_dateUTC(d1)-timedelta(days=3*365)).timestamp()))
        tdelta = timedelta(days=3*365)
        total_count = 0

        total_count_fin = igdb.search2(keyword='',fields='fields id',sort='; sort created_at desc')
        total_count_fin = total_count_fin['count'] if 'count' in total_count_fin else 0

        while int(epoch_to_date(d2)['year']) > 1979:
            filters = [f'created_at > {d2} & created_at < {d1}']#['platforms!=[6]','platforms=[6]']
            db_count = Game.objects.all().count()
            if option == 'count':
                print('total_count',total_count_fin, 'db_count',db_count)
                return
            last_g_d = None
            for filter in filters:
                f_count = igdb.search2(keyword='',filters=filter,fields='fields id',size=500)
                gs = igdb.get_mult_queries(pages=f_count['total_pages'],filters=filter, sort='; sort created_at desc',fields=self.fields,size=500)
                # print(gs)
                # return
                count = len(gs)
                total_count+= count
                print(f'\nPAGES:{f_count["total_pages"]}',f'EXPECTED: {f_count["count"]}',f'GOT:{count}')
                updated = 1
                for g in range(count if count != 0 else 0):
                    # ws = [w for w in gs[g]['websites'] if 'steam' in w['url'].lower()]
                    # ws = (ws[0]['url'] if 'url' in ws[0] else None) if len(ws) > 0 else None
                    #
                    # if ws != None:
                    #     print(self.steam_released_date(ws))

                    created_at = epoch_to_dateUTC(gs[g]['created_at'])

                    # print('\n',created_at)

                    sys.stdout.write(f'\r{g}/{count}')
                    sys.stdout.write("\033[K")
                    if Game.objects.filter(id=gs[g]['id']).exists():
                        last_g_d =  created_at #Game.objects.filter(id=gs[g]['id'])[0].first_release_date
                        if not log:
                            print(f'{g}/{count}', gs[g]['id'], 'exists', last_g_d.date(), f'Total Count:{total_count}')
                        if option == 'add':
                            continue
                    # return
                    has_freld = 'first_release_date' in gs[g]
                    g_d = self.get_rawg_game_details(gs[g],rawg, action=option)

                    if g_d == None:
                        continue
                    _extra = self.extra_ctx(g_d)
                    g_d = _extra['g_d']
                    _extra = _extra['e']

                    def add_only(update=False):
                        nonlocal g_d, _extra, updated
                        if not Game.objects.filter(id=g_d['id']).exists() and db_count != total_count_fin:
                            #ADD HERE
                            g_obj = Game(**g_d)
                            print(f'\n{g}/{count}','NEW', g_d['slug'], g_obj.first_release_date.date(), f'Total Count:{total_count}')
                            g_obj._extra = _extra
                            g_obj.save()
                            last_g_d = created_at
                            # if has_freld:
                            #     last_g_d = g_obj.first_release_date
                        else:
                            if not log:
                                print('\n',g_d['id'], 'exists', g_d['first_release_date'].date())
                            if update:
                                g_obj = Game(**g_d)
                                if not log:
                                    print(f'\n{updated}/{count}','UPDATE', g_d['slug'])
                                [g_d.pop(i,None) for i in ['id','slug']]
                                g_obj._extra = _extra
                                g_obj.save(update_fields=g_d)
                                updated+=1
                                last_g_d = created_at
                            # if has_freld:
                            #     last_g_d =  g_d['first_release_date']

                    def update_only():
                        nonlocal g_d, _extra, updated
                        if Game.objects.filter(id=g_d['id']).exists():
                            g_obj = Game(**g_d)
                            if not log:
                                print(f'\n{updated}/{count}','UPDATE', g_d['slug'])
                            [g_d.pop(i,None) for i in ['id','slug']]
                            g_obj._extra = _extra
                            g_obj.save(update_fields=g_d)
                            updated+=1
                            last_g_d = created_at
                            # if has_freld:
                            #     last_g_d =  g_d['first_release_date']
                    if option == 'add':
                        add_only()
                    elif option == 'update':
                        update_only()
                    elif option == 'add_update':
                        add_only(update=True)
            # print(f'-------------------------------------\n{count}')
            if count != 0:
                d1 = str(int(last_g_d.timestamp()))
                if not log:
                    print('D1',str(last_g_d.date()), 'D2',epoch_to_dateUTC(d2).date())
                else:
                    print(f'{str(last_g_d.date())} - {epoch_to_dateUTC(d2).date()}',end =" ")
                # break
            else:
                d1 = d2
                d2 = str(int((epoch_to_dateUTC(d2) - tdelta).timestamp()))
                if not log:
                    print('D1',epoch_to_dateUTC(d1).date(), 'D2',epoch_to_dateUTC(d2).date())
                else:
                    print(f'{epoch_to_dateUTC(d1).date()} - {epoch_to_dateUTC(d2).date()}',end =" ")
                # break
            # print('\n-----------------------------------------\n')
        print('\ntotal_count',total_count_fin, 'db_count',Game.objects.all().count())
        if log:
            print('\n***********************************END***********************************************\n')

    # def update_games(self):
    #     igdb = IGDB()
    #     rawg = Rawg()
    #     updated = 1
    #     print('Getting games from database')
    #     all_games = Game.objects.all()
    #     ids = [i.id for i in all_games]
    #     print('Getting IGDB updates for the current games in the the database')
    #     gs = igdb.get_multi_games_by_id(ids=ids, fields=self.fields)
    #     count = all_games.count()
    #     for g in range(count):
    #         # print(g, all_games[g].id, gs[g] if g < len(gs) else None)
    #         try:
    #             g_d = self.get_rawg_game_details(gs[g],rawg)
    #             print(g_d==None)
    #             if g_d == None:
    #                 continue
    #             print(f'UPDATED:{updated}/{count}',f'  {g_d["slug"]}')
    #             _extra = self.extra_ctx(g_d)
    #             g_d = _extra['g_d']
    #             _extra = _extra['e']
    #
    #             g_obj = Game(**g_d)
    #             [g_d.pop(i,None) for i in ['id','slug']]
    #             g_obj._extra = _extra
    #             g_obj.save()
    #             updated +=1
    #         except Exception as e:
    #             print(e)
    #             pass
    #
    #     return {'update':f'{updated-1} updated of {all_games.count()}'}


    def update_games(self):
        igdb = IGDB()
        rawg = Rawg()
        updated = 1
        print('Getting games from database')
        all_games = Game.objects.all()
        ids = list(all_games.values_list('id', flat=True))
        print('Getting IGDB updates for the current games in the the database')
        gs = igdb.get_multi_games_by_id2(ids=ids, fields=self.fields)
        print()
        count = all_games.count()
        print(f'{len(gs)} games fetched')
        for g in range(len(gs)):
            try:
                g_d = self.get_rawg_game_details(gs[g],rawg, action='update')

                if g_d == None:
                    continue

                _extra = self.extra_ctx(g_d)
                g_d = _extra['g_d']
                _extra = _extra['e']

                sameln(f'{updated}/{count} UPDATE {g_d["slug"]}')

                g_obj = Game(**g_d)
                [g_d.pop(i,None) for i in ['id','slug']]
                g_obj._extra = _extra
                g_obj.save(update_fields=g_d)

                updated +=1
            except Exception as e:
                print(e)
        print()

        return {'update':f'{updated-1} updated of {all_games.count()}'}

    def get_rawg_game_details(self, i, rawg_obj, action='add_update'):
        extra_cntx = {}
        cover = None
        try:
            cover =  f"https:{str(i['cover']['url']).replace('t_thumb','t_1080p')}" if ('cover' in i and (type(i['cover']) == dict and 'url' in i['cover'])) else None
            extra_cntx['game_cover'] = cover
        except Exception as e:
            extra_cntx['game_cover'] = static('/gamesrec/no-image.png')
            cover = None
        rawg = None
        if i != None:
            g_obj = Game.objects.filter(id=i['id'])
            g_obj = g_obj[0] if g_obj.exists() else None
            if g_obj == None:
                if (not 'first_release_date' in i) and action == 'add' or action == 'add_update':
                    try:
                        ws = [w for w in i['websites'] if 'steam' in w['url'].lower()]
                        ws = (ws[0]['url'] if 'url' in ws[0] else None) if len(ws) > 0 else None
                        if ws != None:
                            rel = self.steam_released_date(ws)
                            if rel == None:
                                return None
                            else:
                                i['first_release_date'] = rel
                                # print(rel)
                        else:
                            return None
                    except Exception as e:
                        return None
                else:
                    return None
            else:
                i['first_release_date'] = int(str(int(g_obj.first_release_date.timestamp())))
            def get_rawg():
                nonlocal rawg_obj, i
                rawg = rawg_obj.get_info(slug=i['slug'], year=epoch_to_date(i['first_release_date'])['year'])
                return rawg
            if cover == None:
                rawg = get_rawg()
                try:
                    cover =  f"https:{str(i['cover']['url']).replace('t_thumb','t_1080p')}" if ('cover' in i and (type(i['cover']) == dict and 'url' in i['cover'])) else None
                    if cover == None:
                        if rawg and 'background_image' in rawg:
                            extra_cntx['game_cover'] = rawg['background_image']
                        else:
                            extra_cntx['game_cover'] = static('/gamesrec/no-image.png')
                    else:
                        extra_cntx['game_cover'] = cover
                except Exception as e:
                    extra_cntx['game_cover'] = static('/gamesrec/no-image.png')
            if (g_obj != None and g_obj.description == None) or (g_obj == None):
                rawg = get_rawg() if rawg == None else rawg
                if not 'storyline' in i:
                    extra_cntx['game_description'] = i['summary'].lstrip().rstrip() if 'summary' in i else ''
                else:
                    extra_cntx['game_description'] = i['storyline'].lstrip().rstrip()
                extra_cntx['game_description'] += rawg['description'] if rawg and 'description' in rawg else ''
            else:
                extra_cntx['game_description'] = g_obj.description
            # soup = BeautifulSoup(extra_cntx['game_description'], 'html.parser')
            # extra_cntx['game_description'] = soup.get_text()
        else:
            if i == None:
                return None
        cntx = {
            'id':i['id'],
            'slug':i['slug'],
            'name':i['name'],
            'rating':round((float(i['rating'])/100)*10,1) if 'rating' in i else 0.0,
            'rating_count': i['rating_count'] if 'rating_count' in i else 0,
            'popularity': i['popularity'] if 'popularity' in i else 0.0,
            'first_release_date': epoch_to_dateUTC(i['first_release_date']),
            'cover': extra_cntx['game_cover'],
            'description': extra_cntx['game_description']
        }
        i.pop('summary',None)
        i.pop('storyline',None)
        i.update(cntx)
        return i
