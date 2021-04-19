from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, JsonResponse, QueryDict, Http404, HttpResponseServerError
from django.core.serializers import serialize
from .models import *
from django.db.models import Q, Count
from .forms import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import auth
import sys
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.contrib.staticfiles.templatetags.staticfiles import static
from .templatetags.media import media
from bs4 import BeautifulSoup
import os
from django.conf import settings
from django.forms.models import model_to_dict
from django.template.defaultfilters import slugify
import pytz
import numpy as np
from django.core.cache import cache
from django.contrib.postgres.search import TrigramSimilarity
from django.urls import resolve
from django.utils import timezone
from django.contrib.sessions.models import Session
from .signals import u_logged_in
from gamesrec.apis.session_info import get_user_info_log
import urllib


from datetime import date,datetime

# from PIL import Image
import requests
from io import BytesIO

from .apis.rawg import Rawg
from .apis.igdb import IGDB

from .apis.helper import *


# Create your views here.

def stores_of_game(request):
    if request.method == 'POST':
        post = request.POST
        r = Rawg()
        stores_r = r.stores_of_game(post.get('id'))
        return JsonResponse(stores_r)

def handler404(request,*args, **kwargs):
    return render(request, 'gamesrec/error_pages/404.html', status=404)

def handler500(request,*args, **kwargs):
    return render(request, 'gamesrec/error_pages/500.html', status=500)

# def api_status(f):
#     def wrapper(*args,**kwargs):
#         # st = IGDB().api_status()
#         if API.objects.all().exists() and IGDB().check_key(): #st['status']:
#             return f(*args,**kwargs)
#         else:
#             return render(args[0], 'gamesrec/error_pages/500.html',{'api': 'Api usage limit reached'})
#     return wrapper

def check_api_status(request,*args, **kwargs):
    st = IGDB().api_status(key=kwargs['key'] if 'key' in kwargs else None)
    return JsonResponse({'api_status':st["json"]},json_dumps_params={'indent': 2})

def logged_in_redirect(f):
    def wrapper(*args, **kwargs):
        if args[0].user.is_authenticated:
            return redirect('gamesrec:index')
        else:
            return f(*args,**kwargs)
    return wrapper

def logged_in(f):
    def wrapper(*args, **kwargs):
        if args[0].user.is_authenticated:
            return f(*args,**kwargs)
        else:
            return redirect('gamesrec:login')
    return wrapper

# @api_status
def index(request, *args, **kwargs):
    context= {}
    return render(request,'gamesrec/index.html',context)

def get_latest(request):
    # lgames = IGDB().latestgames()
    g = Game.objects.filter(first_release_date__lt=(datetime.utcnow()).replace(tzinfo=pytz.utc)).order_by('-first_release_date')
    g = list(g[:12])
    lg = [{**model_to_dict(i), 'url':i.url, 'title':i.title, 'year':i.year, 'first_release_date':i.first_release_date.timestamp()} for i in g]
    return JsonResponse({'games':lg})

def get_personal_recs(request):
    if request.method == 'POST':
        try:
            # if cache.get('p_rec') != None:
            #     return JsonResponse({'result':cache.get('p_rec')})
            import random
            import gamesrec.management.commands.rec as rec
            import time
            start_time = time.time()
            r = rec.personal_recommendations(request.user.id,size=-1)
            # print(f'\n---------------------\nVIEW_Here__1 {time.time()-start_time}\n-------------------------------------\n')
            start_time = time.time()
            if len(r) > 0 and len(r) >= 10:
                r = random.sample(r, 10)  #r[:10]
            else:
                if len(r) == 0:
                    r = []
            gs = []
            for i in r:
                g = Game.objects.filter(id=i)
                if g.exists():
                    g = g[0]
                    # 'rnd_artwork': g.rnd_artwork, 'rnd_screenshot': g.rnd_screenshot,
                    gs.append({**model_to_dict(g), 'url':g.url, 'title': g.title})
            cache.set('p_rec',gs,60)
            # print(f'\n---------------------\nVIEW_Here__2 {time.time()-start_time}\n-------------------------------------\n')
            start_time = time.time()
            return JsonResponse({'result':gs})
        except Exception as e:
            return JsonResponse({'error':str(e)})

def get_genres_and_themes(request):
    res = {}
    res = IGDB().get_genres_and_themes()
    return JsonResponse(res)

def get_igdb_game(request):
    if request.method == 'POST':
        post = request.POST
        res = None
        if post.get('by') == 'id':
            res = IGDB().get_game_by_id(post.get('id'))
        elif post.get('by') == 'slug' :
            res = IGDB().get_game_by_slug(post.get('slug'))
        if res != None:
            if 'cover' in res:
                res['cover']['url'] = 'https:' + res['cover']['url']
        else:
            res = {}
        return JsonResponse(res)

def get_rawg_game(request):
    if request.method == 'POST':
        post = request.POST
        res = None
        rawg = Rawg()
        if post.get('by') == 'id':
            res = rawg.get_info(id=post.get('id'), year=post.get('year'))
        elif post.get('by') == 'slug' :
            res = rawg.get_info(slug=post.get('slug'), year=post.get('year'))
        if res == None:
            res = {}
        return JsonResponse(res)

# @api_status
def game(request, *args,**kwargs):
    if request.method == 'GET':
        # print(kwargs)
        extra_cntx ={}

        exc_details_tabs = ['add_rec','write_review','photos']

        g = Game.objects.filter(id=kwargs['igdb_id'])
        g = g[0] if g.exists() else None
        if g == None:
            raise Http404('Error')
            # return JsonResponse({'result':'Not found'})

        age_ratings = [{'rating':a.rating,'category':a.category} for a in g.age_ratings.all()]
        age_ratings_els = ''
        esrb,pg = None,None
        if len(age_ratings) > 0:
            if age_ratings[0]['category'] == 1:
                esrb,pg = age_ratings[0], age_ratings[1] if len(age_ratings) == 2 else None
            else:
                pg,esrb = age_ratings[0], age_ratings[1] if len(age_ratings) == 2 else None
            if esrb and 'rating' in esrb:
                age_ratings_els += f'<a href="{reverse("gamesrec:search")}?ar_e={esrb["rating"]}"><img class="esrb_{esrb["rating"]} mr-2" /></a>'
            if pg and 'rating' in pg:
                age_ratings_els += f'<a href="{reverse("gamesrec:search")}?ar_p={pg["rating"]}"><img class="pg_{pg["rating"]} mr-2" /></a>'
            extra_cntx['age_ratings_els'] = age_ratings_els

        extra_cntx['game_description'] = g.description
        soup = BeautifulSoup(extra_cntx['game_description'], 'html.parser')
        extra_cntx['game_description'] = soup.get_text()
        soup = BeautifulSoup(extra_cntx['game_description'], 'html.parser')
        g_d_text = len(soup.get_text().lstrip().rstrip())
        g_d_breaks = len(str(soup).split('<br>'))*50
        g_d_text_and_breaks = g_d_text+g_d_breaks
        extra_cntx['has_read_more'] = g_d_text >= 600 or g_d_breaks >= 600 or g_d_text_and_breaks >= 600

        context = {
            'game': {
                **model_to_dict(g),
                'title': g.title,
                'year': g.year,
                'url': g.url,
                'first_release_date': g.first_release_date.date(),
                'rating': g.avg_rating,
                'rating_count': pretty_largenumber_commas(g.avg_rating_count),
                'popularity': round(g.popularity),
                'players': pretty_largenumber_commas(g.players),
            },
            'game_obj': g,
            'tab_name': kwargs['tab_name'] if 'tab_name' in kwargs else None,
            'tab_name_title': get_title(kwargs['tab_name'])  if 'tab_name' in kwargs else '',
            'details': (False if kwargs['tab_name'] in exc_details_tabs  else True) if 'tab_name' in kwargs else True,
            'review_form':ReviewForm(),
            'rec_form': RecForm(),
            'review_exists': Review.objects.filter(game=g.id,user=request.user.pk).exists() if request.user.is_authenticated else -1,
            'reviews': Review.objects.filter(game=g.id),
            'recsu': Rec.objects.filter(Q(game=g.id)|Q(similar_game=g.id)).distinct(),
        }

        if not 'tab_name' in kwargs:
            context['recsu'] = context['recsu'].annotate(likescnt=Count('likes')).order_by('-likescnt')
            context['recsu'] = context['recsu'][:6]
            recsu = {}
            for i in context['recsu']:
                similar = i.similar_game.pk == g.id
                if similar:
                    temp = i.similar_game
                    i.similar_game = i.game
                    i.game = temp
                id_ref = i.similar_game.pk
                if not id_ref in recsu:
                    recsu[id_ref] = i
            context['recsu'] = list(recsu.values())

        if 'tab_name' in kwargs:
            if kwargs['tab_name'] == 'write_review':
                if not request.user.is_authenticated:
                    # messages.error(request, 'Please login to write a review')
                    return redirect(g.reviews_url)
                if (context['review_exists'] != -1 and context['review_exists'] == True):
                    return redirect(g.reviews_url)
            elif kwargs['tab_name'] == 'add_rec':
                if not request.user.is_authenticated:
                    # messages.error(request, 'Please login to add a recommendation')
                    return redirect(g.recs_url)
                # if (context['review_exists'] != -1 and context['review_exists'] == True):
                #     return redirect(g.recs_url)
            elif kwargs['tab_name'] == 'reviews':
                get = request.GET
                page = int(get.get('page')) if 'page' in get else 1
                sort = get.get('sort') if 'sort' in  get else 'helpful_users'
                context['sort_link'] = f'{g.reviews_url}?sort='
                if sort == 'recent' or sort == 'helpful':
                    context['sort'] = sort
                    sort = '-timestamp' if sort == 'recent' else 'helpful_users'
                else:
                    sort = 'helpful_users'

                context['reviews_count'] = context['reviews'].count()
                context['total_pages'] = round(context['reviews_count']/15) if context['reviews_count'] > 15 else 1
                if page > context['total_pages']  or page <= 0:
                    return redirect(g.reviews_url)
                context['reviews'] = context['reviews'].order_by(sort) if sort != 'helpful_users' else context['reviews'].annotate(hcount=Count(sort)).order_by('-hcount')
                context['reviews'] = context['reviews'][(page-1)*15:page*15]
                context['page'] = page
            elif kwargs['tab_name'] == 'recs':
                get = request.GET
                page = int(get.get('page')) if 'page' in get else 1

                context['recsu_count'] = context['recsu'].count()
                context['total_pages'] = round(context['recsu_count']/15) if context['recsu_count'] > 15 else 1
                if page > context['total_pages']  or page <= 0:
                    return redirect(g.recs_url)
                context['recsu'] = context['recsu'].annotate(likescnt=Count('likes')).order_by('-likescnt')
                context['recsu'] = context['recsu'][(page-1)*15:page*15]
                recsu = {}
                for i in context['recsu']:
                    similar = i.similar_game.pk == g.id
                    if similar:
                        temp = i.similar_game
                        i.similar_game = i.game
                        i.game = temp
                    id_ref = i.similar_game.pk
                    if not id_ref in recsu:
                        recsu[id_ref] = i
                        recsu[id_ref].more = []
                    else:
                        recsu[id_ref].more.append(i)
                context['recsu'] = list(recsu.values())
                context['page'] = page

        context.update(extra_cntx)

        return render(request,'gamesrec/game.html',context)
    elif request.method == 'POST':
        post = request.POST
        post._mutable = True
        if 'tab_name' in kwargs:
            if kwargs['tab_name'] == 'write_review':
                if not request.user.is_authenticated:
                    return JsonResponse({'result':'error'})
                post.update({'user':request.user.pk})
                if post.get('completed') == 'True':
                    post.pop('dropped', None)
                    post.update({'dropped': 'False'})
                if post.get('dropped') == 'True':
                    post.pop('completed', None)
                    post.update({'completed': 'False'})
                r_choices = Review.rating_choices
                def rating(rat):
                    for i in r_choices:
                        v = i[1] if i[1] != '-' else 0
                        if float(v) == float(rat):
                            return i[0]
                def update_r(k):
                    rat = post.get(k['h_name']); post.pop(k['h_name'], None); post.update({k['h_name']:rating(rat)})

                [update_r(k) for k in Review.r]
                # print(post)
                rf = ReviewForm(post)
                if rf.is_valid():
                    rf.save()
                    messages.success(request, f'Game review added')
                    return JsonResponse({'result':'success'})
                else:
                    return JsonResponse({'result':'error', 'val':list(rf.errors.items())[0][1][0]})
            elif kwargs['tab_name'] == 'add_rec':
                if not request.user.is_authenticated:
                    return JsonResponse({'result':'error'})
                post.update({'user':request.user.pk})
                rec_exists = Rec.objects.filter(((Q(game=post.get('game')) & Q(similar_game=post.get('similar_game')))|(Q(similar_game=post.get('game')) & Q(game=post.get('similar_game')))),user=request.user.pk).exists()
                if rec_exists:
                    return JsonResponse({'result':'error', 'val':'Recommendation already exists'})
                # print(post)
                rcf = RecForm(post)
                if rcf.is_valid():
                    rcf.save()
                    messages.success(request, f'Game recommendation added')
                    return JsonResponse({'result':'success'})
                else:
                    return JsonResponse({'result':'error', 'val':list(rcf.errors.items())[0][1][0]})


def review_helpful(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        msg = ''
        type = ''
        rev = Review.objects.filter(id=post.get('id'))
        if not rev.exists():
            return JsonResponse({'result':'error'})
        else:
            rev = rev[0]
        user = request.user
        unhelpful_obj = rev.not_helpful_users
        helpful_obj = rev.helpful_users
        unhelpful = user.unhelpful.filter(pk=rev.pk).exists()
        helpful = user.helpful.filter(pk=rev.pk).exists()
        tick_symbol = '<i class="fas fa-check mr-2"></i>'

        if post.get('vote').lower() == 'yes':

            if unhelpful:
                unhelpful_obj.remove(user)

            if helpful:
                type = 'remove'
                msg = 'Cancelled'
                helpful_obj.remove(user)
            else:
                type = 'add'
                msg = 'Marked as helpful'
                helpful_obj.add(user)

        elif post.get('vote').lower() == 'no':
            if helpful:
                helpful_obj.remove(user)

            if unhelpful:
                type = 'remove'
                msg = 'Cancelled'
                unhelpful_obj.remove(user)
            else:
                type = 'add'
                msg = 'Marked as unhelpful'
                unhelpful_obj.add(user)
        rev.save()
        return JsonResponse({'result':'success', 'msg':msg, 'type': type})

def recs_like(request):
    if request.method == 'POST':
        post = request.POST
        rec = Rec.objects.filter(id=post.get('id'))
        if not rec.exists():
            return JsonResponse({'result':'error'})
        else:
            rec = rec[0]
        user = request.user
        likes = rec.likes
        liked = False
        if user.rec_likes.filter(pk=rec.pk).exists():
            likes.remove(user)
        else:
            likes.add(user)
            liked = True
        rec.save()
        return JsonResponse({'cnt':likes.count(), 'liked':liked})

def get_your_rating(request):
    if request.method == 'POST':
        post = request.POST
        r = GameListItem.objects.filter(user__username=post.get('user'),game=int(post.get('game')))
        if r.exists():
            r = r[0]
            return JsonResponse({'rating':str(r.rating_val if r.rating_val != '-' else '0.0')})
        else:
            return JsonResponse({'rating':'0.0'})

def get_game_d(request,*args,**kwargs):
    if request.method == 'POST':
        post = request.POST
        if cache.get(f"game_d_{post.get('id')}") != None:
            return JsonResponse(cache.get(f"game_d_{post.get('id')}"))

        g = Game.objects.filter(id=post.get('id'))
        g = g[0] if g.exists() else None

        if g == None:
            return JsonResponse({'result':'Not found'})

        lookups = [
            # '*',
            'websites.*',
            'id','name', 'slug','first_release_date',
            'involved_companies.*',
            'involved_companies.company.*',
            'involved_companies.company.websites.*',
            'involved_companies.company.developed.id',
            'involved_companies.company.published.id',

            'videos.*', 'screenshots.*',# 'artworks.*',
            'collection.name',# 'collection.games.*',

            # 'external_games.*',

            # 'franchise.*','franchises.*'
        ]

        i = IGDB().get_game_by_id(id=g.id, fields=f'fields {", ".join(lookups)}', collection=True,gm=g)
        rawg = None

        if i != None:
            # pass
            rawg = Rawg().get_info(slug=g.slug, year=str(g.year))
        else:
            return JsonResponse({'result':'Not found 2'})

        context = {
            'igdb': i,
            'rawg': rawg,
            'game_developers': [comp for comp in i['involved_companies'] if comp['developer'] == True] if 'involved_companies' in i else None,
            'game_publishers': [comp for comp in i['involved_companies'] if comp['publisher'] == True] if 'involved_companies' in i else None,
        }
        cache.set(f"game_d_{post.get('id')}", context, 60*30)
        return JsonResponse(context)

def get_game_stats(request):
    if request.method == 'POST':
        post = request.POST
        g = Game.objects.filter(pk=post.get('id'))
        g = g[0] if g.exists() else None
        if g:
            return JsonResponse({'stats':[g.status_stats, g.age_stats, g.score_stats, g.activity_stats]})
        else:
            return JsonResponse({'stats':[]})

def find_friends(request):
    if request.method == 'GET':
        return render(request,'gamesrec/find_friends.html',{})

# @api_status
def search_friends(request):
    if request.method == 'POST':
        post = request.POST
        if 'q' in post:
            q = post.get('q').strip()
            if len(q) == 0:
                return JsonResponse({'matches':[]})
            c = 0
            q1 = []
            o_q = q

            while True:
                q1 = User.objects.annotate(similarity=TrigramSimilarity('username', q)).filter(similarity__gt=0.1).distinct().order_by('-similarity')
                q2 = User.objects.annotate(similarity=TrigramSimilarity('profile__display_name', q)).filter(similarity__gt=0.1).distinct().order_by('-similarity')
                q1 = q1.union(q2).distinct().order_by('-similarity')#[:10]
                ex = {}
                for i in q1.iterator():
                    if not i.pk in ex:
                        ex[i.pk] = i
                q1 = list(ex.values())[:10]
                c = len(q1)
                if c == 0:
                    q = q[:len(q)-1]
                else:
                    break
                if len(q) == 0:
                    break
            m = q1
            m = [ {'id':i.id,'username':i.username, 'display': i.profile.display_name, 'picture': get_profile_pic(i)['picture'], 'url': i.profile.url} for i in m] if len(m) != 0 else []
            return JsonResponse({'matches': m})


# @api_status
def search_autocomplete(request):
    if request.method == 'POST':
        post = request.POST
        if 'q' in post:
            q = post.get('q').strip()
            if len(q) == 0:
                return JsonResponse({'matches':[]})
            c = 0
            q1 = []
            o_q = q
            g_all = Game.objects#.all()
            exc_g = int(post.get('exclude_game')) if 'exclude_game' in post else None

            while True:
                #q1 = g_all.filter(Q(alternativename__name__icontains=q)|Q(name__icontains=q)).distinct()[:10] # OLD
                q1 = Game.objects.annotate(similarity=TrigramSimilarity('name', q)).filter(similarity__gt=0.3).distinct().order_by('-similarity')
                q2 = Game.objects.annotate(similarity=TrigramSimilarity('alternativename__name', q)).filter(similarity__gt=0.3).distinct().order_by('-similarity')
                q1 = q1.union(q2).distinct().order_by('-similarity')#[:10]
                ex = {}
                for i in q1.iterator():
                    if exc_g != None and exc_g == i.pk:
                        continue
                    if not i.pk in ex:
                        ex[i.pk] = i
                q1 = list(ex.values())[:10]
                c = len(q1)
                if c == 0:
                    q = q[:len(q)-1]
                else:
                    break
                if len(q) == 0:
                    break
            m = q1
            def small_cover(cov):
                if cov != None and not 'no-image.png' in cov:
                    cov = cov.replace('t_1080p','t_cover_small')
                return cov
            m = [ {'id':i.id,'name':i.name, 'title': i.title, 'cover':small_cover(i.cover), 'cover_big':i.cover, 'url': i.url} for i in m] if len(m) != 0 else []
            return JsonResponse({'matches': m})

def log_search_query(request):
    if request.method == 'POST':
        r = request
        post = request.POST
        if 'q' in post and len(post.get('q').strip()) != 0:
            if not request.user.is_authenticated:
                r.user = None
            gsq = GameSearchQuery(query=post.get('q').strip().lower(),**get_user_info_log(r))
            gsq.save()
            return JsonResponse({'q':'logged'})
        else:
            return JsonResponse({'q':'not logged'})

def log_friends_search_query(request):
    if request.method == 'POST':
        r = request
        post = request.POST
        u = User.objects.filter(pk=post.get('user_search'))
        if u.exists():
            if not request.user.is_authenticated:
                r.user = None
            fsq = FriendsSearchQuery(searched_user=u[0],**get_user_info_log(r))
            fsq.save()
            return JsonResponse({'q':'logged'})
        else:
            return JsonResponse({'q':'not logged'})

def get_popular_searches(request):
    if request.method == 'POST':
        from django.db.models import Count
        import urllib.parse
        g = GameSearchQuery.objects.values('query').annotate(n=Count("query")).order_by('-n')[:10]
        g = [{'query':i['query'], 'url': f"{reverse('gamesrec:search')}?q={urllib.parse.quote_plus(i['query'])}"} for i in g]
        return JsonResponse({'result':g})

# @api_status
def search(request):
    if request.method == 'GET':
        import time
        start_time = time.time()

        get, context, offset, page = request.GET, {'query' : ''}, 0, 1

        get._mutable = True

        if 'q' in get: context['query'] = get.get('q')

        keyword = get.get('q') if 'q' in get else ''

        page, context['page'] = int(get.get('page')) if 'page' in get else page, page

        filters = SearchFilterMgr().get_filters2(get)

        if len(filters['json'].keys()) == 0 and filters['sort'] == None and filters['created'] == '' and not 'page' in get:
            if 'q' in get and len(get.get('q').strip()) != 0:
                m = Game.objects.filter(Q(alternativename__name__iexact=get.get('q'))|Q(name__iexact=get.get('q'))).distinct() #Game.objects.filter(name__iexact=get.get('q'))
                cnt = m.count()
                if cnt > 0:
                    if cnt == 1:
                        m = m[0]
                        return redirect(m.url)
        import hashlib

        enc_check = hashlib.md5(str.encode(json.dumps({'search':get}))).hexdigest()

        if cache.get(enc_check) != None:
            cntx = cache.get(enc_check)
            cntx['data']['cache'] = True
            return render(request,'gamesrec/search.html',cntx)

        r,res = None, None

        q = (get.get('q') if len(get.get('q')) != 0 else None) if 'q' in get else None

        def tpages(count):
            import math
            num_of_pages = count/20
            if num_of_pages < 1 and num_of_pages > 0:
                return 1
            else:
                m = math.modf((count/20))
                num_of_pages = int(m[1]) + 1
                if m[0] == 0:
                    num_of_pages -=1
                return num_of_pages

        qu = Game.objects

        for i in filters['filters_db']:
            qu = qu.filter(i)
        else:
            qu = qu.filter(Q())

        so = ''
        r = qu

        if filters['sort_db'] != None:
            so = filters['sort_db']
            if type(filters['sort_db']) == dict:
                if 'q_obj' in filters['sort_db']:
                    r = r.filter(filters['sort_db']['q_obj'])
                    so = filters['sort_db']['val']

        if q != None:
            q1 = r.annotate(similarity=TrigramSimilarity('name', q)).filter(similarity__gt=0.2).distinct()
            q2 = r.annotate(similarity=TrigramSimilarity('alternativename__name', q)).filter(similarity__gt=0.2).distinct()
            r = q1.union(q2).distinct()
            r = r.order_by(so) if so != '' else r.order_by('-similarity')

            from collections import OrderedDict
            ex = OrderedDict()
            for i in r.iterator():
                if not i.pk in ex:
                    ex[i.pk] = i
            r = list(ex.values())
            res = {
                'count': len(r),
                'result': r[(20 * (page-1)):(20 * (page-1))+20]
            }
        else:
            if so != '':
                r = r.order_by(so)
            else:
                r = r.order_by('-first_release_date')
            res = {
                'count': r.count(),
                'result': r[(20 * (page-1)):(20 * (page-1))+20]
            }

        res['total_pages'] = tpages(res['count'])
        res['keyword'] = q
        res['page'] = page
        res['offset'] = 20 * (page-1)

        if res['total_pages'] != 0 and page > res['total_pages']:
            raise Http404('error')

        filters_json = filters['json']
        sortby = filters['sort']
        filters = filters['created']
        filters = filters if len(filters.strip()) != 0 else None

        def get_game_obj(g):
            return {
                **model_to_dict(g),
                'title': g.title,
                'year': g.year,
                'url': g.url,
                'first_release_date': g.first_release_date.timestamp(),
                'description': g.description[:214] + ('...' if not g.description[:214].endswith('.') else '..'),
                'platforms': [{'name':f.name} for f in g.platforms.all()],
                'videos':None#i['videos'] if 'videos' in i else None,
            }

        res['result'] = [get_game_obj(i) for i in res['result']]

        context['data'] = res
        context['filters'] = filters_json
        context['filters_length'] = len(filters_json.keys())

        cache.set(enc_check, context, 60*2)

        return render(request,'gamesrec/search.html',context)

def get_igdb_trailers(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        mg = None
        mg_cache = False
        result = {}

        try:
            gids = [int(i) for i in json.loads(post.get('ids'))]

            import hashlib

            enc_check = hashlib.md5(str.encode(json.dumps({'igdb_trailers':gids}))).hexdigest()

            if cache.get(enc_check) != None:
                mg = cache.get(enc_check)
                mg_cache = True

            if mg_cache == False:
                mg = IGDB().get_multi_games_by_id(ids=gids, fields='fields id, videos.*', id_as_key=True)
                cache.set(enc_check,mg, 60*15)

            for i in gids:
                result[i] = mg[i]['videos'] if i in mg and 'videos' in mg[i] else None
        except Exception as e:
            # print(e)
            pass
        return JsonResponse(result)

def add_or_edit_bool(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        b = []
        if request.user.is_authenticated:
            l = list(json.loads(post.get('gids')))
            gliset = request.user.gamelistitem_set
            b = [gliset.filter(game_id=i).exists() for i in l]
        else:
            b = [False for i in range(20)]
        return JsonResponse({'result':b})

def darkmode_toggle(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        dark_mode = False
        if request.user.is_authenticated:
            request.user.profile.dark_mode = not request.user.profile.dark_mode
            request.user.profile.save()
            dark_mode = request.user.profile.dark_mode
            return JsonResponse({'dark_mode':dark_mode})
        else:
            if post.get('dark_mode') == '1' or post.get('dark_mode') == '0':
                dark_mode = post.get('dark_mode')
                r = JsonResponse({'dark_mode':dark_mode})
                r.set_cookie('dark_mode',value=dark_mode,httponly=True)
                return r
            else:
                return JsonResponse({'dark_mode':dark_mode})

def letter(request, *args,**kwargs):
    import os

    def projpath(file):
        import os
        from django.conf import settings
        return os.path.abspath(os.path.join(settings.PROJ_DIR, file))

    if os.name == 'nt':
        from .lib.pillow.windows_pillow.PIL import Image, ImageDraw, ImageFont
    else:
        from .lib.pillow.linux_pillow.PIL import Image, ImageDraw, ImageFont
    import string

    colors = [
    '#de14ab',
    '#3280ec',
    '#78ef27',
    '#8181da',
    '#2bfedd',
    '#4ae8ad',
    '#735709',
    '#5239f2',
    '#caed71',
    '#330b30',
    '#6adea1',
    '#389642',
    '#2a5ff6',
    '#cc1896',
    '#a5d73e',
    '#e2e24d',
    '#e2e24d',
    '#78872e',
    '#56f265',
    '#5a8c54',
    '#ffdd33',
    '#544591',
    '#cecc3f',
    '#79900a',
    '#2e5ea8',
    '#0cbc31',
    '#23dd54',
    ]

    response = HttpResponse(content_type="image/png")

    size = 64

    if len(kwargs) == 2:
        if 'size' in kwargs:
            size = int(kwargs['size'])
            del kwargs['size']

    l = kwargs['name'][0].upper() if 'name' in kwargs and len(kwargs) == 1 else '?'
    l = l if l in string.ascii_uppercase else '?'

    cindx = string.ascii_uppercase.index(l) if l != '?' else len(colors)-1

    img = Image.new('RGB', (size, size), color = colors[cindx])

    font_size = int((30/64)*size)

    font_loc = os.path.abspath(os.path.join(os.path.dirname(__file__),'OpenSans-Regular.ttf'))#projpath(static('gamesrec/OpenSans-Regular.ttf')[1:])

    try:
        fnt = ImageFont.truetype(font_loc, font_size)
        w, h = fnt.getsize(l)
        d = ImageDraw.Draw(img)
        pt = int((5/64)*size)
        d.text((((size-w)/2),((size-h)/2)-pt), l, font=fnt, fill='white')

        img.save(response, 'png')

        return response
    except Exception as e:
        return response

@logged_in_redirect
def signin(request):
    if request.method == 'POST':
        post = request.POST
        form = LoginForm(request,post)
        valid = form.is_valid()
        msg = ''
        if valid:
            auth.login(request,form.get_user())
            u = form.get_user()
            u_logged_in.send(u.__class__, instance=u, request=request)
            msg = 'Successfully logged in!'
            messages.success(request, msg)
        else:
            msg = list(form.errors.items())[0][1][0]
        return JsonResponse({'valid':valid, 'msg':msg, 'redirect': request.user.profile.url if request.user.is_authenticated else None})
    else:
        context= {
            'form':LoginForm()
        }
        return render(request,'gamesrec/signin.html',context)

@logged_in_redirect
def register(request):
    if request.method == 'POST':
        post = request.POST
        form = RegistrationForm(post)
        valid = form.is_valid()
        msg = ''
        if valid:
            form.save()
            msg = 'You have been successfully registered!!'
            messages.success(request, msg)
        else:
            msg = list(form.errors.items())
        return JsonResponse({'valid':valid, 'msg':msg, 'redirect': reverse('gamesrec:registration_complete')})
    else:
        form = RegistrationForm()
        context= {
            'form':form
        }
        return render(request,'gamesrec/signup.html',context)


def get_profile_pic(user):
    picture = None
    try:
        picture = media(user.profile.picture.url) if user.profile.picture.url else None
    except Exception as e:
        picture = None
    obj = {
        'picture': picture if picture != None else reverse('gamesrec:letter',kwargs={'name':user.username}),
        'picture_300': picture if picture != None else reverse('gamesrec:letter_size',kwargs={'name':user.username, 'size':300})
    }
    return obj


def profile(request, *args, **kwargs):
    if request.method == 'GET':
        user = None
        try:
            if (not 'username' in kwargs) or ('username' in kwargs and len(kwargs['username']) == 0):
                if request.user.is_authenticated:
                    kwargs['username'] = request.user.username
                else:
                    return redirect('gamesrec:index')

            user = User.objects.get(username__iexact=kwargs['username'])
        except Exception as e:
            raise Http404('Error')
        context = {
            'user' : user,
            'profile_tab': kwargs['profile_tab'] if 'profile_tab' in kwargs else None
        }

        context.update(get_profile_pic(user))

        def get_qpath(id, obj):
            o = obj.objects.get(id=id)
            return {'id':o.id, 'name':o.name, 'qpath':o.qpath}
        if not 'profile_tab' in kwargs:
            context['title'] = f"{user.username}'s Profile"

        if 'profile_tab' in kwargs:
            if kwargs['profile_tab'] == 'stats':
                context['title'] = f"Stats - {user.username}'s Profile"
                context['stats'] = {}
                q1 = GameListItem.objects.filter(Q(user=user) & (Q(status=1) | Q(status=3) | Q(status=4)))
                q1.values('game__genres__name').distinct().annotate(n=models.Count("pk")).order_by('-n')
                q2 = q1.values('game__genres__id','game__genres__name').distinct().annotate(count=models.Count("pk")).order_by('-count')
                q2 = list(q2)
                genres = [{**get_qpath(i['game__genres__id'],Genre), 'count': i['count'], 'percent': f"{i['count'] if i['count'] < 100 else 100}%"} for i in q2]
                context['stats']['genres'] = genres

                q1.values('game__themes__name').distinct().annotate(n=models.Count("pk")).order_by('-n')
                q2 = q1.values('game__themes__id','game__themes__name').distinct().annotate(count=models.Count("pk")).order_by('-count')
                q2 = list(q2)
                themes = [{**get_qpath(i['game__themes__id'],Theme), 'count': i['count'], 'percent': f"{i['count'] if i['count'] < 100 else 100}%"} for i in q2]
                context['stats']['themes'] = themes

                # print(context['stats'])
            elif kwargs['profile_tab'] == 'reviews':
                context['title'] = f"{user.username}'s Reviews"
                get = request.GET
                page = int(get.get('page')) if 'page' in get else 1
                sort = get.get('sort') if 'sort' in  get else 'helpful_users'
                context['sort_link'] = f'{user.profile.reviews_url}?sort='
                if sort == 'recent' or sort == 'helpful':
                    context['sort'] = sort
                    sort = '-timestamp' if sort == 'recent' else 'helpful_users'
                else:
                    sort = 'helpful_users'

                context['reviews'] = Review.objects.filter(user=user.pk)
                context['reviews'] = context['reviews'].order_by(sort) if sort != 'helpful_users' else context['reviews'].annotate(hcount=Count(sort)).order_by('-hcount')
                context['reviews_count'] = context['reviews'].count()
                context['total_pages'] = round(context['reviews_count']/15) if context['reviews_count'] > 15 else 1
                if page > context['total_pages']  or page <= 0:
                    return redirect(user.profile.reviews_url)
                context['reviews'] = context['reviews'][(page-1)*15:page*15]
                context['page'] = page
            elif kwargs['profile_tab'] == 'recs':

                context['title'] = f"{user.username}'s Recommendations"

                get = request.GET
                page = int(get.get('page')) if 'page' in get else 1

                context['recsu'] = Rec.objects.filter(user=user.pk)

                context['recsu_count'] = context['recsu'].count()
                context['total_pages'] = round(context['recsu_count']/15) if context['recsu_count'] > 15 else 1
                if page > context['total_pages']  or page <= 0:
                    return redirect(g.recs_url)
                context['recsu'] = context['recsu'].annotate(likescnt=Count('likes')).order_by('-likescnt')
                context['recsu'] = context['recsu'][(page-1)*15:page*15]
                context['page'] = page
            elif kwargs['profile_tab'] == 'edit_review':
                if (request.user.is_authenticated and  user != request.user) or not request.user.is_authenticated:
                    return redirect(user.profile.reviews_url)
                rev_id = kwargs['id']
                rev = Review.objects.filter(id=rev_id)
                if not rev.exists():
                    return redirect(request.user.profile.reviews_url)
                context['title'] = f"Edit Review for '{rev[0].game.title}'"
                rev_f = ReviewForm(instance=rev[0])
                r_vals = Review.r_vals
                def star_and_val(indx):
                    val = r_vals[indx]
                    val = val if val != '-' else 0.0
                    v = {
                        'value': val,
                        'star':float(val)*10
                    }
                    return v
                context['review_rating_ids_names_values'] = [{**i, **star_and_val(rev_f[i['h_name']].value())} for i in Review.r]
                context['review_form'] = rev_f
                context['review'] = rev[0]
            elif kwargs['profile_tab'] == 'edit_rec':
                if (request.user.is_authenticated and  user != request.user) or not request.user.is_authenticated:
                    return redirect(user.profile.recs_url)
                rec_id = kwargs['id']
                rec = Rec.objects.filter(id=rec_id)
                if not rec.exists():
                    return redirect(request.user.profile.recs_url)
                context['title'] = f"Edit Rec '{rec[0].game.name}' ~ '{rec[0].similar_game.name}'"
                rec_f = RecForm(instance=rec[0])
                context['rec_form'] = rec_f
                context['rec'] = rec[0]
            elif kwargs['profile_tab'] == 'history':
                context['title'] = f"{user.username}'s History"

        return render(request,'gamesrec/profile.html',context)
    else:
        post = request.POST
        post._mutable = True
        if 'profile_tab' in kwargs:
            if kwargs['profile_tab'] == 'edit_review':
                if not request.user.is_authenticated:
                    return JsonResponse({'result':'error'})
                post.update({'user':request.user.pk})
                rev = Review.objects.filter(id=kwargs['id'])[0]
                if post.get('completed') == 'True':
                    post.pop('dropped', None)
                    post.update({'dropped': 'False'})
                if post.get('dropped') == 'True':
                    post.pop('completed', None)
                    post.update({'completed': 'False'})
                r_choices = Review.rating_choices
                def rating(rat):
                    for i in r_choices:
                        v = i[1] if i[1] != '-' else 0
                        if float(v) == float(rat):
                            return i[0]
                def update_r(k):
                    rat = post.get(k['h_name']); post.pop(k['h_name'], None); post.update({k['h_name']:rating(rat)})

                [update_r(k) for k in Review.r]
                # print(post)
                rf = ReviewForm(post, instance=rev)
                if rf.is_valid():
                    rf.save()
                    messages.success(request, f'Game review updated')
                    return JsonResponse({'result':'success'})
                else:
                    messages.error(request,list(rf.errors.items())[0][1][0])
                    # print(list(rf.errors.items()))
                    return JsonResponse({'result':'error'})
            elif kwargs['profile_tab'] == 'edit_rec':
                if not request.user.is_authenticated:
                    return JsonResponse({'result':'error'})
                post.update({'user':request.user.pk})
                rec = Rec.objects.filter(id=kwargs['id'])[0]
                post.update({'game':rec.game.pk,  'similar_game':rec.similar_game.pk})
                rf = RecForm(post, instance=rec)
                if rf.is_valid():
                    rf.save()
                    messages.success(request, f'Game recommendation updated')
                    return JsonResponse({'result':'success'})
                else:
                    messages.error(request,list(rf.errors.items())[0][1][0])
                    # print(list(rf.errors.items()))
                    return JsonResponse({'result':'error'})

def remove_review(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        try:
            rev = Review.objects.filter(pk=post.get('id'))
            if rev.exists():
                t = ''
                try:
                    t = rev[0].game.name[:15]
                    t = '<span style={style}>{name}</span>'.format(style='"font-style:italic;font-weight:900;"',name=f"'{t}...'")
                except Exception as e:
                    pass
                rev[0].delete()
                messages.success(request, f"<span>Review for {t} &nbsp;&nbsp; has been removed</span>")
                return JsonResponse({'result':'success','redirect':request.user.profile.reviews_url})
            else:
                return JsonResponse({'result':'error'})
        except Exception as e:
            # print(e)
            return JsonResponse({'result':'error2'})

def remove_rec(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        try:
            rec = Rec.objects.filter(pk=post.get('id'))
            if rec.exists():
                rec[0].delete()
                messages.success(request, f"<span>Recommendation has been removed</span>")
                return JsonResponse({'result':'success','redirect':request.user.profile.recs_url})
            else:
                return JsonResponse({'result':'error'})
        except Exception as e:
            # print(e)
            return JsonResponse({'result':'error2'})

def recent_recommendations(request, *args, **kwargs):
    if request.method == 'GET':
        context = {}
        get = request.GET
        page = int(get.get('page')) if 'page' in get else 1

        context['title'] = f"Recommendations - Page {page}"

        context['recsu'] = Rec.objects.all().order_by('-timestamp')

        context['recsu_count'] = context['recsu'].count()
        context['total_pages'] = round(context['recsu_count']/15) if context['recsu_count'] > 15 else 1
        if page > context['total_pages']  or page <= 0:
            return redirect(g.recs_url)
        # context['recsu'] = context['recsu'].annotate(likescnt=Count('likes')).order_by('-likescnt')
        context['recsu'] = context['recsu'][(page-1)*15:page*15]
        context['page'] = page
        return render(request,'gamesrec/recs.html',context)

def comments_test(request, *args, **kwargs):
    context = {
        'co':Comment.objects.all(),
    }
    return render(request,'gamesrec/comments.html',context)


def comment_rate(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        msg = ''
        type = ''
        c = Comment.objects.filter(id=post.get('id'))
        if not c.exists():
            return JsonResponse({'result':'error'})
        else:
            c = c[0]
        user = request.user
        dislikes = c.dislikes
        likes = c.likes
        c_dislikes = user.c_dislikes.filter(pk=c.pk).exists()
        c_likes = user.c_likes.filter(pk=c.pk).exists()
        tick_symbol = '<i class="fas fa-check mr-2"></i>'

        if post.get('rate').lower() == 'yes':

            if c_dislikes:
                dislikes.remove(user)

            if c_likes:
                type = 'remove'
                msg = 'Cancelled'
                likes.remove(user)
            else:
                type = 'add'
                msg = 'Liked'
                likes.add(user)

        elif post.get('rate').lower() == 'no':
            if c_likes:
                likes.remove(user)

            if c_dislikes:
                type = 'remove'
                msg = 'Cancelled'
                dislikes.remove(user)
            else:
                type = 'add'
                msg = 'Disliked'
                dislikes.add(user)
        c.save()
        l_count = pretty_large_short(c.likes.count())
        dl_count = pretty_large_short(c.dislikes.count())
        return JsonResponse({'result':'success', 'msg':msg, 'type': type, 'count': {'likes':l_count, 'dislikes': dl_count}})

def comment_get_obj_t(args):
    type_name = args.get('type_name') if 'type_name' in args else None
    if type_name == 'GameComment':
        return GameComment
    elif type_name ==  'ReviewComment':
        return ReviewComment
    else:
        return Comment

def comment_add_obj_t(obj, args):
    type_name = args.get('type_name') if 'type_name' in args else None
    t_id = args.get('t_id') if 't_id' in args else None
    if type_name == 'GameComment':
        t = Game.objects.filter(pk=t_id)
        t = t[0] if t.exists() else None
        obj.game = t
        return obj
    elif type_name ==  'ReviewComment':
        t = Review.objects.filter(pk=t_id)
        t = t[0] if t.exists() else None
        obj.review = t
        return obj
    else:
        return obj

def get_comments_type(args, **kwargs):
    type_name = args.get('type_name') if 'type_name' in args else None
    t_id = args.get('t_id') if 't_id' in args else None
    if type_name == 'GameComment':
        kwargs['game'] = t_id
        return GameComment.objects.filter(**kwargs)
    elif type_name == 'ReviewComment':
        kwargs['review'] = t_id
        return ReviewComment.objects.filter(**kwargs)
    else:
        return Comment.objects.filter(**kwargs)

def comment(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        from urllib.parse import unquote
        obj_t = comment_get_obj_t(post)
        c = obj_t(user=request.user, text=unquote(post.get('text')))
        c = comment_add_obj_t(c, post)
        c.save()
        return JsonResponse({'ok':'ok'})

def reply(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        from urllib.parse import unquote
        obj_t = comment_get_obj_t(post)
        c = obj_t(user=request.user, text=unquote(post.get('text')))
        p = obj_t.objects.filter(pk=post.get('id'))
        if p.exists():
            c.parent = p[0]
            if 'mention_id' in post:
                mc = obj_t.objects.filter(pk=post.get('mention_id'))
                if mc.exists():
                    mc = mc[0]
                    c.mention = mc.user
            c = comment_add_obj_t(c, post)
            c.save()
            return JsonResponse({'result':'ok'})
        else:
            return JsonResponse({'result':'error'})

def get_comment_txtarea(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        c = Comment.objects.filter(pk=post.get('id'))
        return JsonResponse({'data':str(CommentForm(instance=c[0])) if c.exists() else None})

def load_comments(request, *args, **kwargs):
    from django.template.defaultfilters import linebreaks
    if request.method == 'POST':
        post = request.POST
        offset = int(post.get('offset')) if 'offset' in post else 0
        c = get_comments_type(post, level=0)
        c_count = c.count()
        c = c.order_by('-timestamp')[offset:offset+20]
        def get_comment_details(i):
            reps = i.get_children()
            reps_count = reps.count()
            first_rep = None
            if reps_count == 1:
                first_rep = reps[0].user.username
            return {
                'id': i.pk,'username': i.user.username,
                'text': str(CommentForm(instance=i)),
                'profile': i.user.profile.url,
                'timestamp': pretty_dt_timestamp(time=i.timestamp),
                'has_replies': reps_count,
                'first_reply': first_rep,
                'picture': get_profile_pic(i.user)['picture'],
                'user_liked': request.user in i.likes.all() if request.user.is_authenticated else False,
                'user_disliked': request.user in i.dislikes.all() if request.user.is_authenticated else False,
                'likes_count': pretty_large_short(i.likes.count()),
                'dislikes_count': pretty_large_short(i.dislikes.count()),
            }
        c = [get_comment_details(i) for i in c]
        return JsonResponse({'root_comments':c, 'count':c_count})

def load_replies(request, *args, **kwargs):
    from django.template.defaultfilters import linebreaks
    if request.method == 'POST':
        post = request.POST
        offset = int(post.get('offset')) if 'offset' in post else 0
        p = Comment.objects.filter(pk=post.get('id'))
        # print(post)
        if p.exists():
            p = p[0]
            c = p.get_children().order_by('timestamp')[offset:offset+11]
            def get_reply_details(i):
                return {
                    'id': i.pk,
                    'username': i.user.username,
                    'text': str(CommentForm(instance=i)),
                    'mention': f'<a class="text-primary link_color mr-1" href="{i.mention.profile.url}">@{i.mention.username}</a>' if i.mention else None,
                    'profile': i.user.profile.url,
                    'timestamp': pretty_dt_timestamp(time=i.timestamp),
                    'has_replies':i.get_children().count(),
                    'picture': get_profile_pic(i.user)['picture'],
                    'user_liked': request.user in i.likes.all() if request.user.is_authenticated else False,
                    'user_disliked': request.user in i.dislikes.all() if request.user.is_authenticated else False,
                    'likes_count': pretty_large_short(i.likes.count()),
                    'dislikes_count': pretty_large_short(i.dislikes.count()),
                }
            c = [get_reply_details(i) for i in c]
            return JsonResponse({'root_comments':c})
        else:
            return JsonResponse({'root_comments':[]})

def update_comment(request, *args, **kwargs):
    if request.method == 'POST':
        from urllib.parse import unquote
        post = request.POST
        post._mutable = True
        c = Comment.objects.filter(user=request.user, pk=post.get('id'))
        if c.exists():
            c = c[0]
        else:
            return JsonResponse({'result':'error'})
        if post.get('action') == 'text_update':
            c.text = unquote(post.get('text'))
            c.save()
            return JsonResponse({'result':'text_success', 'data':str(CommentForm(instance=c))})
        elif post.get('action') == 'delete':
            try:
                c.delete()
                return JsonResponse({'result':'delete_success', 'msg':f'{post.get("type").capitalize()} deleted'})
            except Exception as e:
                return JsonResponse({'result':'delete_error', 'msg':'Failed to delete'})

def get_replies_count_msg(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        c = Comment.objects.filter(pk=post.get('id'))
        reps = c[0].get_children()
        count = reps.count()
        msg = {
            'show': f'View {count} replies',
            'hide': f'Hide {count} replies',
            'count': count
        }
        if count == 1:
            msg['show'] = f'View reply from {reps[0].user.username}'
            msg['hide'] = f'Hide reply'
        return JsonResponse(msg)

def get_comments_count(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        c = get_comments_type(post)
        count = c.count()
        return JsonResponse({'count':count, 'pretty_count':pretty_largenumber_commas(count)})

def gameslist(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        return JsonResponse({'ok':'ok'})
    else:
        user = None
        try:
            if (not 'username' in kwargs) or ('username' in kwargs and len(kwargs['username']) == 0):
                if request.user.is_authenticated:
                    kwargs['username'] = request.user.username
                else:
                    return redirect('gamesrec:index')

            user = User.objects.get(username__iexact=kwargs['username'])
        except Exception as e:
            raise Http404('Error')
        context = {
            'user' : user,
            'list_type': kwargs['list_type'] if 'list_type' in kwargs else None,
            'status_link_path': reverse('gamesrec:gameslist',kwargs={'username':user.username})
        }
        return render(request,'gamesrec/gameslist.html',context)

def get_lists_count(request):
    if request.method == 'POST':
        post = request.POST
        gli = GameListItem.objects.filter(Q(user__username=post.get('user')))
        st_names = GameListItem.status_names
        st_slugs = [slugify(i.lower()) for i in st_names]
        l = []
        def get_list(indx):
            nonlocal l, st_names
            l.append({st_slugs[indx]: gli.filter(Q(status=indx)).count() })
        for i in range(len(st_names)):
            get_list(i)
        return JsonResponse({'lists':l})

def get_games_lists(request):
    if request.method == 'POST':
        post = request.POST
        gli = GameListItem.objects.filter(Q(user__username=post.get('user')))
        st_names = GameListItem.status_names
        st_slugs = [slugify(i.lower()) for i in st_names]
        l = []
        def get_list(indx):
            nonlocal l, st_names
            gs = [{**model_to_dict(j),'status':j.status_val, 'rating': str(j.rating_val) if str(j.rating_val) != '-' else '0.0', 'game':{**model_to_dict(j.game),'url':j.game.url,'year':j.game.year,'title':j.game.title}} for j in list(gli.filter(Q(status=indx)))]
            l.append({st_slugs[indx]:gs})
        if str(post.get('list_type')) != 'None':
            get_list(st_slugs.index(post.get('list_type')))
        else:
            for i in range(len(st_names)):
                get_list(i)
        # if len(l) == 1:
        #     l = l[0]
        #     l = l[list(l.keys())[0]]
        return JsonResponse({'lists':l})
    else:
        return JsonResponse({'lists':None})

def recent_list_updates(request):
    if request.method == 'POST':
        post = request.POST
        user = None
        try:
            user = post.get('user') if 'user' in post else None
            user = user if user != None and len(user) != 0 else None
            if (user == None):
                if request.user.is_authenticated:
                    user = request.user.username
                else:
                    return JsonResponse({'result':'Error1'})
            user = User.objects.get(username__iexact=user)
        except Exception as e:
            return JsonResponse({'result':'Error2'})
        list_updates = GameListItem.objects.filter(user=user).order_by('-updated_at')[:10]
        def get_game_d(i):
            from datetime import date, datetime
            l = model_to_dict(i)
            l['game'] = model_to_dict(i.game)
            l['game']['url'] = i.game.url

            l['timestamp'] =  pretty_dt_timestamp(time=i.updated_at.timestamp()) if i.updated_at.date() == datetime.today().date() else datetime.strftime(i.updated_at.date(), '%b %d, %Y')
            l['status_val'] = i.status_val
            return l
        return JsonResponse({'result': [get_game_d(i) for i in list(list_updates)]})

def last_online(request):
    if request.method == 'POST':
        post = request.POST
        user = User.objects.filter(username=post.get('user'))
        user = user[0] if user.exists() else None
        r_user = request.user
        try:
            from datetime import datetime, date
            from django.utils import timezone
            u = User.objects.get(username=user.username)
            if r_user.username == user.username:
                u.last_online = timezone.now()
                u.save()
            return JsonResponse({'last_online':pretty_dt_timestamp(time=u.last_online)})
        except Exception as e:
            return JsonResponse({'last_online':None})

@login_required
def account_settings(request):
    if request.method == 'POST':
        post = request.POST
        post._mutable = True
        # print(post)
        post.pop('picture',None)
        if 'date_of_birth' in post and post.get('date_of_birth'):
            dob = post.get('date_of_birth')
            post.pop('date_of_birth', None)
            post.update({'date_of_birth':datetime.strftime(datetime.strptime(dob,'%d %B, %Y'), '%Y-%m-%d')})
            post.update({'dob':datetime.strftime(datetime.strptime(dob,'%d %B, %Y'), '%Y-%m-%d')})
        # print(post)
        post.update({'username':request.user.username,'email':request.user.email})
        form_p = AccountSettingsForm_Profile(post,instance=request.user.profile)
        form_u =  AccountSettingsForm_User(post,instance=request.user)
        # print('PROFILE_FORM:',form_p.is_valid(), 'USER_FORM:',form_u.is_valid())
        try:
            if form_p.is_valid() and form_u.is_valid():
                form_p.save()
                form_u.save()
                return JsonResponse({'result':'success'})
            else:
                return JsonResponse({'result':'error1'})
        except Exception as e:
            return JsonResponse({'result':'error2'})
    else:
        path_name = resolve(request.path_info).url_name
        if path_name == 'account_settings':
            p = request.user.profile
            if p.display_name == None or (p.display_name != None and p.display_name.strip() == ''):
                p.display_name = request.user.username
                p.save()
            u = request.user
            if u.dob != None:
                u.dob = datetime.strftime(datetime.strptime(str(u.dob),'%Y-%m-%d'),'%d %B, %Y')
            profile_path = request.user.profile.url
            profile_path = profile_path.replace(request.user.username, f'<b>{request.user.username}</b>')
            context = {
                'form_p': AccountSettingsForm_Profile(instance=p),
                'form_u': AccountSettingsForm_User(instance=u, initial={'date_of_birth':u.dob}),
                'full_profile_url': f"{request.scheme}://{request.META['HTTP_HOST']}{profile_path}",
                'path_name': path_name,
                'title': 'Account Settings'
            }
        elif path_name == 'account_privacy':
            context = {
                'path_name': path_name,
                'title': 'Security & Privacy'
            }
        return render(request,'gamesrec/account_settings.html',context)

def upload_picture(request):
    if request.method == 'POST':
        post = request.POST
        files = request.FILES
        # print(post)
        # print(files)
        if 'picture' in files:
            # print(files.get('picture'))
            if len(str(request.user.profile.picture).strip()) != 0:
                os.remove(os.path.join(settings.MEDIA_ROOT,request.user.profile.picture.name))
            request.user.profile.picture = files.get('picture')
            request.user.profile.save()
            return JsonResponse({'updated':request.user.profile.picture.url})

def remove_picture(request):
    if request.method == 'POST':
        post = request.POST
        if 'remove' in post:
            if len(str(request.user.profile.picture).strip()) != 0:
                try:
                    os.remove(os.path.join(settings.MEDIA_ROOT,request.user.profile.picture.name))
                    request.user.profile.picture = ''
                    request.user.profile.save()
                    return JsonResponse({'result':'success','picture':get_profile_pic(request.user)['picture']})
                except Exception as e:
                    return JsonResponse({'result':'error'})
            else:
                return JsonResponse({'result':'error'})


def atl_edit_form(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        if 'game' in post:
            context = {}
            if request.user.is_authenticated:
                atl_g = GameListItem.objects.filter(user=request.user, game=int(post.get('game')))
                context['atl_form'] = GameListItemForm() if not atl_g.exists() else GameListItemForm(instance=atl_g[0])
            else:
                context['atl_form'] = ''
            return render(request,'gamesrec/components/atl_edit_form_modal_component.html',context)
    raise Http404('Error')

def list_action(request, *args, **kwargs):
    if request.method == 'POST':
        post = request.POST
        post._mutable = True
        g = None
        try:
            g = Game.objects.get(id=int(post.get('game')))
        except Exception as e:
            return JsonResponse({'result':'error1'})

        post.update({'user':request.user.pk})

        # print(post)

        gi = None
        try:
            gi = GameListItem.objects.filter(game=int(post.get('game')), user=request.user)
        except Exception as e:
            pass

        if 'method' in post and post.get('method') == 'get':
            j = None
            if gi.exists():
                j = list(gi.values('status','rating','notes'))[0]
            return JsonResponse({'result': j})


        gi = gi[0] if gi.exists() else None

        # print(GameListItemForm(post).errors.items())

        f = GameListItemForm(post) if gi == None else GameListItemForm(post,instance=gi)
        if f.is_valid():
            if 'method' in post and post.get('method') == 'delete':
                try:
                    gi.delete()
                    return JsonResponse({'result':'deleted'})
                except Exception as e:
                    return JsonResponse({'result':'error2'})
            if gi != None:
                f.save(commit=False)
                gi.save()
            else:
                f.save()
            return JsonResponse({'result':'created_updated'})
        else:
            return JsonResponse({'result':'error3'})


def list_item_rating_history(request):
    if request.method == 'POST':
        post = request.POST
        if 'game' in post:
            gi = GameListItem.objects.filter(game=int(post.get('game')), user=request.user)
            if not gi.exists():
                return JsonResponse({'result':[]})

            history_q = GameListItemHistory.objects.filter(game_list_item=gi[0]).order_by('-timestamp')
            history = list(history_q.values('id','status','rating','timestamp'))

            def add_rating(i):
                gih = history_q.filter(pk=i['id'])[0]
                i['rating'] = str(gih.rating_val)
                i['status'] = str(gih.status_val)
                i['timestamp'] = str(gih.timestamp_pretty)
                i.pop('id',None)
                return i
            history = [add_rating(i) for i in history]
            return JsonResponse({'result': history})
        else:
            return JsonResponse({'result':'error'})

@logged_in
def logout(request):
    auth.logout(request)
    return redirect('gamesrec:login')

def registration_complete(request):
    return render(request,'gamesrec/account/registration_complete.html',{})


def _test_html(request):
    # return render(request,'gamesrec/account/password_change_done.html',{})
    # return render(request,'gamesrec/account/password_change.html',{})
    # return render(request,'gamesrec/account/password_reset_complete.html',{})
    # return render(request,'gamesrec/account/password_reset_confirm.html',{})
    # return render(request,'gamesrec/account/password_reset_done.html',{})
    # return render(request,'gamesrec/account/password_reset.html',{})
    # return render(request,'gamesrec/account/password_reset_email.html',{'uid':1, 'token':1})
    return render(request,'gamesrec/account/registration_complete.html',{})


def get_user_sessions(request):
    if request.method == 'POST':
        c_key = request.session.session_key
        def get_inf(s):
            inf = {
                'id':s.pk,
                'ip_address': s.ip_address,
                'device': s.device,
                'browser': s.browser,
                'location': s.location,
                'last_active': pretty_dt_timestamp(s.active_timestamp),
                'is_current':  c_key == s.session_key
            }
            if inf['last_active'] == 'just now':
                inf['last_active'] = 'Active'
            return inf
        sessions = [get_inf(i) for i in UserSession.objects.filter(user=request.user).order_by('-created')]
        return JsonResponse({'devices':sessions})

def remove_session(request):
    if request.method == 'POST':
        post = request.POST
        c_key = request.session.session_key
        s = UserSession.objects.filter(user=request.user, pk=post.get('id'))
        if s.exists():
            s = s[0]
            current = s.session_key == c_key
            s.end_session()
            return JsonResponse({'result':True, 'current':current, 'redirect':reverse('gamesrec:login'), 'msg': 'Device removed'})
        else:
            return JsonResponse({'result':False})

def get_user_actions(request):
    if request.method == 'POST':
        from datetime import timedelta
        t = {}
        ua = UserAction.objects.filter(timestamp__gte=(timezone.now()- timedelta(minutes=60)), timestamp__lte=timezone.now()+timedelta(minutes=60)).order_by('timestamp').values_list('timestamp', flat=True)

        for i in ua:
            i = datetime.strftime(i, "%Y-%m-%d %H:%M:%S.%f")
            if not str(i) in ua:
                t[str(i)] = 1
            else:
                t[str(i)] += 1
        r = [[k,t[k]]for k in t.keys()]
        return JsonResponse({'userActions':r})

def analytics(request):
    if request.method == 'POST':
        post = request.POST
        def activeCount():
            c = 0
            for i in UserSession.objects.all():
                if i.is_active_now:
                    c+=1
            return c

        def most_active_users():
            u = User.objects.filter(is_admin=False)
            def get_u_inf(i):
                return {
                    'id':i.id,
                    'username':i.username,
                    'display': i.profile.display_name,
                    'picture': get_profile_pic(i)['picture'],
                    'url': i.profile.url,
                    'actions_count':UserAction.objects.filter(user=i).count()
                }
            l = [get_u_inf(i) for i in u]
            return sorted(l, key=lambda k: k['actions_count'],reverse=True)[:10]

        def get_devices_inf():
            from gamesrec.apis.session_info import location, device
            u_l = UsageLog.objects.order_by().values('ip_address', 'user_agent').distinct()
            b_s = {}
            d_s = {}
            l_s = {}
            for i in u_l:
                d_i = device(i['user_agent'], json=True)
                loc = location(i['ip_address'])
                loc = loc if loc != None else 'Others'
                b = d_i['browser']
                d = d_i['device']

                if not b in b_s:
                    b_s[str(b)] = 1
                else:
                    b_s[str(b)] += 1

                if not loc in l_s:
                    l_s[str(loc)] = 1
                else:
                    l_s[str(loc)] += 1

                if not str(d) in d_s:
                    d_s[str(d)] = 1
                else:
                    d_s[str(d)] += 1

            cnt = {
                'b_s': sum(b_s.values()),
                'd_s': sum(d_s.values()),
                'l_s': sum(l_s.values()),
            }

            b_s = [{'name':str(i), 'y':round((b_s[i]/cnt['b_s'])*100, 1), 'cnt':b_s[i]} for i in b_s.keys()]
            d_s = [{'name':str(i), 'y':round((d_s[i]/cnt['d_s'])*100, 1), 'cnt':d_s[i]} for i in d_s.keys()]
            l_s = [{'name':str(i), 'y':round((l_s[i]/cnt['l_s'])*100, 1), 'cnt':l_s[i]} for i in l_s.keys()]

            return {
                'browsers':{'data':b_s,'count':cnt['b_s']},
                'devices':{'data':d_s,'count':cnt['d_s']},
                'locations':{'data':l_s,'count':cnt['l_s']}
            }

        data = {
            'games_count': pretty_largenumber_commas(Game.objects.all().count()),
            'activeUsersCount': pretty_largenumber_commas(activeCount()),
            'usersCount': pretty_largenumber_commas(User.objects.all().count()),
            'userActionsCount': pretty_largenumber_commas(UserAction.objects.all().count()),
            'mostActiveUsers':most_active_users(),
            'siteUsage':pretty_largenumber_commas(UsageLog.objects.all().count()),
            'device_inf':get_devices_inf(),
        }
        return JsonResponse(data)
    elif request.method == 'GET':
        get = request.GET
        # UserSession.
        return render(request,'gamesrec/analytics.html',{})

def load_history(request):
    if request.method == 'POST':
        post = request.POST
        if post.get('history_type') == 'comment':
            offset = int(post.get('offset')) if 'offset' in post else 0
            c = GameComment.objects.filter(user=request.user)
            c_count = c.count()
            c = c.order_by('-timestamp')[offset:offset+20]
            def get_comment_details(i):
                return {
                    'id': i.pk,
                    'username': i.user.username,
                    'text': str(CommentForm(instance=i)),
                    'timestamp': pretty_dt_timestamp(time=i.timestamp),
                    'game_id': i.game.pk,
                    'game_title': i.game.title,
                    'game_url':i.game.url,
                }
            c = [get_comment_details(i) for i in c]
            return JsonResponse({'root_comments':c, 'count':c_count})

def export_list(request):
    if request.method == 'POST':
        post = request.POST
        if not request.user.is_authenticated:
            return HttpResponse('Invalid Request')

        gli = GameListItem.objects.filter(Q(user=request.user))
        st_names = GameListItem.status_names
        st_slugs = [slugify(i.lower()) for i in st_names]
        l = []
        x = 1

        import csv

        def get_list(indx):
            nonlocal l, st_names
            def get_list_itm(j):
                def norm_descr(tx):
                    return BeautifulSoup(tx, 'html.parser').get_text()
                return (
                    j.game.cover,
                    j.game.title,
                    f"{request.scheme}://{request.META['HTTP_HOST']}{j.game.url}",
                    norm_descr(j.game.description),
                    str(j.rating_val) if str(j.rating_val) != '-' else '0.0',
                    j.notes,
                    j.status_val,
                )
            for j in list(gli.filter(Q(status=indx))):
                l.append(get_list_itm(j))

        def export(_l, fname):
            nonlocal x
            response = HttpResponse(content_type='text/csv')
            dt_now = datetime.strftime(datetime.now(), '[%d-%m-%Y]_%H_%M_%S')
            response['Content-Disposition'] = f'attachment; filename="{fname}_{dt_now}.csv"'
            response.write(u'\ufeff'.encode('utf8'))
            writer = csv.writer(response)
            writer.writerow(['#','Cover', 'Title', 'Link', 'Description','Your rating', 'Your notes', 'Status'])
            for g in _l:
                writer.writerow([x] + list(g))
                x+=1
            return response

        if post.get('status') in st_slugs:
            indx = st_slugs.index(post.get('status'))
            get_list(indx)
            return export(l, st_names[indx])
        else:
            if post.get('status') == 'all':
                for i in range(len(st_names)):
                    get_list(i)
                return export(l, 'All')

        return HttpResponse('Invalid Request')
