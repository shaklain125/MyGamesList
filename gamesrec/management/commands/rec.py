from django.core.management.base import BaseCommand

from gamesrec.models import *
from django.db.models import Q
from django.forms.models import model_to_dict

import json
import os

from datetime import date, datetime
import sys
from django.core.cache import cache

def random_recommendations(size=-1):
    def get_rec2(g_s, u_s):
        import pandas as pd
        import numpy as np
        from scipy.sparse import csr_matrix
        from sklearn.neighbors import NearestNeighbors

        games_df = pd.json_normalize(g_s) #pd.read_json('igdb_games_rating.json')
        rating_df = pd.json_normalize(u_s) #pd.read_json('users.json')

        # print(games_df.shape)
        # print(games_df.head())
        # print(rating_df.head())

        merge_df = pd.merge(games_df,rating_df,left_on='id',right_on='gameid')

        # print(merge_df.head())
        # print(games_df.shape, rating_df.shape)

        combine_game_rating = merge_df.dropna(axis = 0, subset = ['id'])
        game_ratingCount = combine_game_rating.groupby(by=['id'])
        game_ratingCount = game_ratingCount['rating_y'].count().reset_index()
        game_ratingCount = game_ratingCount.rename(columns = {'rating_y': 'rating_count'})[['id', 'rating_count']]

        # exit()

        # print(game_ratingCount.head())

        rating_with_rating_count = combine_game_rating.merge(game_ratingCount, left_on = 'id', right_on = 'id', how = 'left')

        # print(rating_with_rating_count.head())

        pd.set_option('display.float_format', lambda x: '%.3f' % x)

        # print(game_ratingCount['rating_count'].describe())

        rating_pop = rating_with_rating_count.query('rating_count_y >= 50') #games_df.query('rating_count >= 50')

        # print(rating_pop.head())

        # print(rating_pop.shape)

        # print(rating_pop)

        games_fe_df = rating_pop.pivot_table(index='id',columns='userid',values='rating_y').fillna(0) #rating_pop.pivot_table(index='name',values='rating').fillna(0)

        # print(games_fe_df)

        metric = 'cosine'#'correlation'
        model_knn = NearestNeighbors(metric = metric, algorithm = 'brute')
        if metric == 'cosine':
            model_knn.fit(csr_matrix(games_fe_df.values))
        else:
            model_knn.fit(games_fe_df.values)

        # print(games_fe_df.shape)

        query_index = np.random.choice(games_fe_df.shape[0])

        # print(query_index)

        distances, indices = model_knn.kneighbors(games_fe_df.iloc[query_index,:].values.reshape(1, -1), n_neighbors = 21)

        # print(games_fe_df.head())

        game_ids = []

        for i in range(0, len(distances.flatten())):
            id = games_fe_df.index[query_index] if i == 0 else games_fe_df.index[indices.flatten()[i]]
            game_ids.append(id)
            # row = games_df.loc[games_df['id'] == id]
            # name = row['name'].values[0]
            # if i == 0:
            #     print('Recommendations for {0}:\n'.format(name))
            # else:
            #     print('{0}: {1}, with distance of {2}:'.format(i, name, distances.flatten()[i]))
            if size != -1 and i == size:
                return game_ids
        return game_ids
    rec = []
    try:
        gs = list(Game.objects.all().values('id', 'name', 'slug', 'rating', 'rating_count'))
        users = json.loads(UserRatings.objects.all()[0].data)
        rec = get_rec2(g_s=gs,u_s=users)
        rec = rec if size == -1 else rec[:size+1]
    except Exception as e:
        # print('ERROR ', e)
        pass
    return rec

def personal_recommendations(user_id, size=-1):
    from gamesrec.models import UserRatings, User
    import json
    import pandas as pd
    import numpy as np
    from scipy.sparse import csr_matrix
    from sklearn.neighbors import NearestNeighbors
    import time

    def get_rec(g_s, u_s,user):
        start_time = time.time()
        games_df = None #pd.json_normalize(g_s) #pd.read_json('igdb_games_rating.json')
        rating_df = None #pd.json_normalize(u_s) #pd.read_json('users.json')

        cache_val = False

        if cache.get('prec_data') != None:
            prec_data = cache.get('prec_data')
            games_df = prec_data[0]
            rating_df = prec_data[1]
            print('cache - games_df')
            cache_val = True

        if not cache_val:
            games_df = pd.json_normalize(g_s)
            rating_df = pd.json_normalize(u_s)
            cache.set('prec_data', [games_df, rating_df], 60*30)


        print(f'\n---------------------\nHere__2 {time.time()-start_time}\n-------------------------------------\n')
        start_time = time.time()

        merge_df = pd.merge(games_df,rating_df,left_on='id',right_on='gameid')

        combine_game_rating = merge_df.dropna(axis = 0, subset = ['id'])
        game_ratingCount = combine_game_rating.groupby(by=['id'])
        game_ratingCount = game_ratingCount['rating_y'].count().reset_index()
        game_ratingCount = game_ratingCount.rename(columns = {'rating_y': 'rating_count'})[['id', 'rating_count']]

        rating_with_rating_count = combine_game_rating.merge(game_ratingCount, left_on = 'id', right_on = 'id', how = 'left')

        rating_pop = rating_with_rating_count.query('rating_count_y >= 50')

        games_fe_df = rating_pop.pivot_table(index='id',columns='userid',values='rating_y')

        games_fe_df_T = games_fe_df.T

        # print(games_fe_df_T)

        pivot_temp = games_fe_df_T.fillna(-1)
        pivot_table = games_fe_df_T.fillna(0)
        pivot_table = pivot_table.apply(np.sign)

        # rated,rated_indexes = {},{}
        # notrated,notrated_indexes = {},{}
        #
        # for i,row in pivot_temp.iterrows():
        #     rows = [x for x in range(0, len(games_fe_df_T.columns))]
        #     combine = list(zip(row.index,row.values,rows))
        #     rated_rows,not_rated_rows = [],[]
        #     for x,y,z in combine:
        #         if int(y) != -1:
        #             rated_rows.append((x,z))
        #         if not int(y) > 0:
        #             not_rated_rows.append((x,z))
        #     rated_indexes[i] = [i[1] for i in rated_rows]
        #     rated[i] = [i[0] for i in rated_rows]
        #     notrated_indexes[i] = [i[1] for i in not_rated_rows]
        #     notrated[i] = [i[0] for i in not_rated_rows]

        print(f'\n---------------------\nHere__2.1 {time.time()-start_time}\n-------------------------------------\n')
        start_time = time.time()


        rated_indexes = {}
        rows = [x for x in range(0, len(games_fe_df_T.columns))]

        for i,row in pivot_temp.iterrows():
            rated_indexes[i] = [z for x,y,z in list(zip(row.index,row.values,rows)) if int(y) != -1]

        print(f'\n---------------------\nHere__3 {time.time()-start_time}\n-------------------------------------\n')
        start_time = time.time()

        model_knn = NearestNeighbors(n_neighbors=20, metric = 'cosine', algorithm = 'brute')
        knn_fit = model_knn.fit(pivot_table.T.values)
        distances, indices = knn_fit.kneighbors(pivot_table.T.values)

        # item_dic = {}
        # for i in range(len(pivot_table.T.index)):
        #     item_dic[pivot_table.T.index[i]] = pivot_table.T.index[indices[i]].tolist()

        # print(item_dic)
        # print(len(rated[user]))

        def accuracy_and_errors_predictions():
            def root_mean_sq_error(prediction, ground_truth):
                from sklearn.metrics import mean_squared_error
                from math import sqrt
                prediction = prediction[ground_truth.nonzero()].flatten()
                ground_truth = ground_truth[ground_truth.nonzero()].flatten()
                return sqrt(mean_squared_error(prediction,ground_truth))

            dist = 1-distances
            predictions = dist.T.dot(pivot_table.T.values)/ np.array([np.abs(dist.T).sum(axis=1)]).T
            ground_truth = pivot_table.T.values[dist.argsort()[0]]

            error_rate = root_mean_sq_error(predictions,ground_truth)
            print('Accuracy {0:.3f}'.format(100-error_rate))
            print('root_mean_sq_error {0:.5f}'.format(error_rate))


        accuracy_and_errors_predictions()

        def get_top_recs(user):
            nonlocal start_time
            if not user in rated_indexes:
                return []

            def name(i):
                return games_df.loc[games_df['id'] == i]['name'].values[0]
            toprecs = {}
            v = rated_indexes[user]
            item_index = [j for i in indices[v] for j in i]
            item_dist = [j for i in distances[v] for j in i]
            combine = list(zip(item_dist,item_index))
            di = {i:d for d,i in combine if i not in v}
            zi = list(zip(di.keys(),di.values()))
            so = sorted(zi, key=lambda x: x[1])
            toprecs[user] = [(pivot_table.columns[i],d) for i,d in so]
            game_ids = []
            c = 1
            print(f'\n---------------------\nHere__3.1 {time.time()-start_time}\n-------------------------------------\n')
            start_time = time.time()
            for i in toprecs[user]:
                # print('{0} {1} {2} with similarity: {3:.4f}'.format(c,name(i[0]),'ID:{0}'.format(i[0]),1-i[1]))
                game_ids.append(i[0])
                if size != -1 and c == size:
                    return game_ids
                c+=1
            return game_ids #toprecs[user]

        return get_top_recs(user)
    rec = []
    try:
        import time
        start_time = t_start_time = time.time()


        gs = []
        users = []
        if cache.get('prec_data') != None:
            pass
        else:
            gs = list(Game.objects.all().values('id', 'name', 'slug', 'rating', 'rating_count'))
            users = json.loads(UserRatings.objects.all()[0].data)
        print(f'\n---------------------\nHere__1 {time.time()-start_time}\n-------------------------------------\n')
        start_time = time.time()

        rec = get_rec(g_s=gs,u_s=users,user=user_id)
        rec = rec if size == -1 else rec[:size]
        print(f'\n---------------------\nHere__Last {time.time()-t_start_time}\n-------------------------------------\n')
        start_time = time.time()
    except Exception as e:
        print('ERROR ', e)
        pass
    return rec

def update(log=False):
    db_all_users = User.objects.all().values('id')
    db_all_users = [u['id'] for u in db_all_users]
    def get_rnd_ratings(gameid, m_rating, rating_count):
        import random
        from random import seed, gauss
        seed(m_rating)
        r = []
        c = 1
        while len(r) < rating_count:
            if not c in db_all_users:
                sample = gauss(m_rating, 0.05)
                if sample >= 0 and sample <= 10:
                    sample = round(sample,1)#one_dp(sample)#
                    d = {
                        'userid':c,
                        'rating':sample,
                        'gameid':gameid
                    }
                    r.append(d)
                    c+=1
            else:
                # print(f'{c} userid exists')
                c+=1
        return r

    def get_db_users(i):
        db_users = list(GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=3) | Q(status=4)) & Q(game__id=i['id'])))
        db_users = [{'userid':d.user.id, 'rating':d.rating_val if d.rating_val != '-' else 0.0, 'gameid':d.game.id} for d in db_users]
        return db_users

    gs = list(Game.objects.all().values('id', 'name', 'slug', 'rating', 'rating_count'))
    users = []
    cnt = 1
    t_cnt = len(gs)
    for i in gs:
        r = get_rnd_ratings(i['id'],i['rating'],i['rating_count']) + get_db_users(i)
        if len(users) == 0:
            users = r
        else:
            users += r
        s = sum([j['rating'] for j in r])
        precis = 0.0 if int(s) == 0 else (s if int(i['rating_count']) == 0 else s/i['rating_count'])
        # print([j['rating'] for j in r][:5], round(i['rating'],1),round(precis,1), i['slug'], i['id'])
        if not log:
            sys.stdout.write(f"\r{cnt}/{t_cnt} ID:{i['id']} {i['slug']}")
            sys.stdout.write("\033[K")
        cnt+=1
    if log:
        print(f"[{str(datetime.now())}] {cnt-1}/{t_cnt}")
    else:
        print()
    u_r_objs = list(UserRatings.objects.all())
    if len(u_r_objs) == 0:
        u_r = UserRatings(data=json.dumps(users))
        u_r.save()
    else:
        u_r = u_r_objs[0]
        u_r.data = json.dumps(users)
        u_r.save(update_fields=['data'])

def update_guest_recs():
    import json
    r = random_recommendations(size=10)
    if len(r) > 0:
        r = r[1:]
        r = [int(i) for i in r]
        gu_rec = list(GuestRecommendations.objects.all())
        if len(gu_rec) == 0:
            g_r = GuestRecommendations(data=json.dumps(r))
            g_r.save()
        else:
            g_r = gu_rec[0]
            g_r.data = json.dumps(r)
            g_r.save(update_fields=['data'])
        return r
    else:
        return []


class Command(BaseCommand):
    missing_args_message = """
    \nOptions:\n
     update             ---- updates user ratings
     guest              ---- updates guest recommendations
     rnd                ---- get random recommendations\n
    -get [user_id]      ---- gets recommendations for uesr
    """

    def add_arguments(self, parser):
        parser.add_argument('cmd', nargs='?')
        parser.add_argument('-get', nargs='?', help='gets recommendations for user id')

    def handle(self, *args, **options):
        if options['cmd'] == 'update':
            update()
            return
        elif options['cmd'] == 'rnd':
            r = random_recommendations(size=10)
            print(r[1:] if len(r) > 0 else [])
            return
        elif options['cmd'] == 'guest':
            print(update_guest_recs())
            return
        if options['get']:
            print('Getting recommendations...')
            print(personal_recommendations(int(options['get']), size=10))
