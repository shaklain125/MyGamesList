from django import template
from django.shortcuts import reverse
from django.template.defaultfilters import escapejs

from tag_parser.basetags import BaseAssignmentNode, BaseNode
from gamesrec.models import *
from gamesrec.forms import *
import pytz
from datetime import datetime, date

register = template.Library()

def fa_icon(name):
    if name is None:
        return None
    return '<i class="{0}"></i>'.format(name)

def link_item(name, url, icon=None, sublinks=None):
    return {'name' : name,'url' : url,'icon' : fa_icon(icon), 'sublinks': sublinks}

@register.simple_tag
def navbar_items():
    links = [
        link_item('Home',reverse('gamesrec:index'),'far fa fa-home'),
        link_item('Explore','',None,[
            link_item('Top Games',f"{reverse('gamesrec:search')}?so=5"),
            link_item('Most Popular Games',f"{reverse('gamesrec:search')}?so=2"),
            link_item('Newest',f"{reverse('gamesrec:search')}?so=3"),
            link_item('Recommendations',f"{reverse('gamesrec:recent_recommendations')}"),
            link_item('Find Friends',f"{reverse('gamesrec:find_friends')}"),
            link_item('Analytics',f"{reverse('gamesrec:analytics')}"),
        ]),
        link_item('About','',None,[
            link_item('FAQ',''),
        ]),
    ]
    return links

@register.tag('last_online')
class last_online(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        user = context['user']
        r_user = context['request'].user
        try:
            from datetime import datetime, date
            from django.utils import timezone
            from ..models import User
            u = User.objects.get(username=user.username)
            if r_user.username == user.username:
                u.last_online = timezone.now()
                u.save()
            return u.last_online
        except Exception as e:
            return None


@register.simple_tag(takes_context=True)
def profile_picture_64(context, user):
    from .media import media
    from django.contrib.staticfiles.templatetags.staticfiles import static
    if not context['request'].user.is_authenticated and user == context['request'].user:
        return static('gamesrec/avatar.png')
    letter_url = reverse('gamesrec:letter',kwargs={'name':user.username})
    try:
        picture = media(user.profile.picture.url) if user.profile.picture.url else None
        return picture if picture != None else letter_url
    except Exception as e:
        # print(e)
        return letter_url

@register.tag('check_has_profile_pic')
class check_has_profile_pic(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        user = context['request'].user
        try:
            return True if user.profile.picture.url else False
        except Exception as e:
            return False

# @register.tag('is_dark_mode')
# class is_dark_mode(BaseAssignmentNode):
#
#     def get_value(self, context, *tag_args, **tag_kwargs):
#         user = context['request'].user
#         try:
#             if user.is_authenticated and user.profile.dark_mode:
#                 return True
#             else:
#                 return False
#         except Exception as e:
#             return False



# @register.simple_tag
# def platforms():
#     platforms = [
#         {"id": 6,"abbreviation": "PC","name": "PC (Windows)"},
#         {"id": 160,"name": "Nintendo eShop"},
#         {"id": 9,"abbreviation": "PS3","name": "PlayStation 3"},
#         {"id": 165,"abbreviation": "PlayStation VR","name": "PlayStation VR"},
#         {"id": 12,"abbreviation": "X360","name": "Xbox 360"},
#         {"id": 48,"abbreviation": "PS4","name": "PlayStation 4"},
#         {"id": 46,"abbreviation": "Vita","name": "PlayStation Vita"},
#         {"id": 5,"abbreviation": "Wii","name": "Wii"},
#         {"id": 38,"abbreviation": "PSP","name": "PlayStation Portable"},
#         {"id": 137,"name": "New Nintendo 3DS"},
#         {"id": 37,"abbreviation": "3DS","name": "Nintendo 3DS"},
#         {"id": 130,"abbreviation": "Switch","name": "Nintendo Switch"},
#         {"id": 49,"abbreviation": "XONE","name": "Xbox One"},
#         {"id": 162,"abbreviation": "Oculus VR","name": "Oculus VR"},
#         {"id": 20,"abbreviation": "NDS","name": "Nintendo DS"}
#     ]
#     return platforms

@register.tag('platforms')
class platforms(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        from django.core.serializers import serialize
        import json
        platforms = [
            {"id": 6,"abbreviation": "PC","name": "PC (Windows)"},
            {"id": 160,"name": "Nintendo eShop"},
            {"id": 9,"abbreviation": "PS3","name": "PlayStation 3"},
            {"id": 165,"abbreviation": "PlayStation VR","name": "PlayStation VR"},
            {"id": 12,"abbreviation": "X360","name": "Xbox 360"},
            {"id": 48,"abbreviation": "PS4","name": "PlayStation 4"},
            {"id": 46,"abbreviation": "Vita","name": "PlayStation Vita"},
            {"id": 5,"abbreviation": "Wii","name": "Wii"},
            {"id": 38,"abbreviation": "PSP","name": "PlayStation Portable"},
            {"id": 137,"name": "New Nintendo 3DS"},
            {"id": 37,"abbreviation": "3DS","name": "Nintendo 3DS"},
            {"id": 130,"abbreviation": "Switch","name": "Nintendo Switch"},
            {"id": 49,"abbreviation": "XONE","name": "Xbox One"},
            {"id": 162,"abbreviation": "Oculus VR","name": "Oculus VR"},
            {"id": 20,"abbreviation": "NDS","name": "Nintendo DS"}
        ]
        return list(Platform.objects.all().values()) #platforms


@register.tag('game_modes')
class game_modes(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        from django.core.serializers import serialize
        import json
        modes = [
            {"id": 3,"name": "Co-operative", 'abbreviation':'Co-operative'},
            {"id": 1,"name": "Single player", 'abbreviation':'Single Player'},
            {"id": 2,"name": "Multiplayer", 'abbreviation':'Multiplayer'},
            {"id": 5,"name": "MMO", 'abbreviation':'Massively Multiplayer Online'},
            {"id": 4,"name": "Split screen", 'abbreviation':'Split Screen'}
        ]
        return list(GameMode.objects.all().values()) #modes

@register.tag('genres_and_themes')
class genres_and_themes(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        from django.core.serializers import serialize
        import json
        genres_and_themes = {'genres': [{'id': 31, 'name': 'Adventure'}, {'id': 33, 'name': 'Arcade'}, {'id': 4, 'name': 'Fighting'}, {'id': 25, 'name': "Hack and slash/Beat 'em up"}, {'id': 32, 'name': 'Indie'}, {'id': 7, 'name': 'Music'}, {'id': 30, 'name': 'Pinball'}, {'id': 8, 'name': 'Platform'}, {'id': 2, 'name': 'Point-and-click'}, {'id': 9, 'name': 'Puzzle'}, {'id': 26, 'name': 'Quiz/Trivia'}, {'id': 10, 'name': 'Racing'}, {'id': 11, 'name': 'Real Time Strategy (RTS)'}, {'id': 12, 'name': 'Role-playing (RPG)'}, {'id': 5, 'name': 'Shooter'}, {'id': 13, 'name': 'Simulator'}, {'id': 14, 'name': 'Sport'}, {'id': 15, 'name': 'Strategy'}, {'id': 24, 'name': 'Tactical'}, {'id': 16, 'name': 'Turn-based strategy (TBS)'}, {'id': 34, 'name': 'Visual Novel'}], 'themes': [{'id': 41, 'name': '4X (explore, expand, exploit, and exterminate)'}, {'id': 1, 'name': 'Action'}, {'id': 28, 'name': 'Business'}, {'id': 27, 'name': 'Comedy'}, {'id': 31, 'name': 'Drama'}, {'id': 34, 'name': 'Educational'}, {'id': 42, 'name': 'Erotic'}, {'id': 17, 'name': 'Fantasy'}, {'id': 22, 'name': 'Historical'}, {'id': 19, 'name': 'Horror'}, {'id': 35, 'name': 'Kids'}, {'id': 43, 'name': 'Mystery'}, {'id': 32, 'name': 'Non-fiction'}, {'id': 38, 'name': 'Open world'}, {'id': 40, 'name': 'Party'}, {'id': 33, 'name': 'Sandbox'}, {'id': 18, 'name': 'Science fiction'}, {'id': 23, 'name': 'Stealth'}, {'id': 21, 'name': 'Survival'}, {'id': 20, 'name': 'Thriller'}, {'id': 39, 'name': 'Warfare'}]}
        return  {'genres':list(Genre.objects.all().values()),'themes': list(Theme.objects.all().values())} #genres_and_themes


@register.simple_tag
def age_ratings():
    pegi = [
        {'id':1, 'name':'PEGI: 3'},
        {'id':2, 'name':'PEGI: 7'},
        {'id':3, 'name':'PEGI: 12'},
        {'id':4, 'name':'PEGI: 16'},
        {'id':5, 'name':'PEGI: 18'},
    ]
    esrb = [
        {'id':6, 'name':'ESRB: Rating Pending'},
        {'id':7, 'name':'ESRB: Early Childhood'},
        {'id':8, 'name':'ESRB: Everyone'},
        {'id':9, 'name':'ESRB: Everyone 10+'},
        {'id':10, 'name':'ESRB: Teen'},
        {'id':11, 'name':'ESRB: Mature'},
        {'id':12, 'name':'ESRB: Adults Only'},
    ]
    return {'pegi':pegi,'esrb':esrb}

@register.tag('player_perspectives')
class player_perspectives(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        from django.core.serializers import serialize
        import json
        persps = [
            {"id": 4,"name": "Side view"},
            {"id": 2,"name": "Third person"},
            {"id": 5,"name": "Text"},
            {"id": 7,"name": "Virtual Reality"},
            {"id": 1,"name": "First person"},
            {"id": 3,"name": "Bird view"},
            {"id": 6,"name": "Aural"}
        ]
        return list(Perspective.objects.all().values()) #persps

@register.simple_tag
def sort_options():
    o = ['Relevance','Most popular','Newest','Released date','Top rated',] #'Top ranked'
    return o


@register.simple_tag
def released_range():
    from datetime import datetime,date
    #(date.today().year) - ((date.today().year) % 100)
    return {'from':1980,'to':date.today().year+10}

@register.filter
def toJson(value):
    import json
    return escapejs(json.dumps(value))

@register.filter
def subtract(value, arg):
    return value - arg

@register.filter
def value(value,arg):
    if arg in value:
        return value[arg]
    else:
        return None

@register.filter
def rating_one_dp(value):
    def change_to_5star(i):
        return (float(i)/100)*5
    try:
        import math
        return str(math.floor(float(change_to_5star(value))*10)/10)
    except Exception as e:
        return '0.0'
    return escapejs(json.dumps(value))

@register.filter
def subtract(value, arg):
    if type(arg) == list:
        arg = len(arg)
    if type(value) == list:
        value = len(value)
    return value - arg

@register.filter
def add_arr_len(value, arg):
    if type(arg) == list:
        arg = len(arg)
    elif type(arg) != int:
        arg = 0
    if type(value) == list:
        value = len(value)
    elif type(value) != int:
        value = 0
    return value + arg

@register.filter
def replace(value,args):
    r = [i.strip() for i in args.split(',')]
    return value.replace(r[0],r[1])

@register.filter
def get_total_s_shots_count(value, args):
    c = 0
    if value and 'screenshots' in value and args and 'screenshots' in args:
        c = len(value['screenshots']) + len(args['screenshots'])
    else:
        if value and 'screenshots' in value:
            c = len(value['screenshots'])
        else:
            if args and 'screenshots' in args:
                c = len(args['screenshots'])
    return c

@register.filter
def get_total_videos_count(value, args):
    c = 0
    if value and 'videos' in value and args and 'youtube_videos' in args:
        c = len(value['videos']) + len(args['youtube_videos'])
    else:
        if value and 'videos' in value:
            c = len(value['videos'])
        else:
            if args and 'youtube_videos' in args:
                c = len(args['youtube_videos'])
    return c

@register.filter
def toString(value):
    return str(value)

@register.filter
def pretty_dt(value):
    from ..apis.helper import pretty_dt_timestamp
    # print(value)
    return pretty_dt_timestamp(time=value)

@register.tag('dob_date_year_only')
class dob_date_year_only(BaseNode):

    def render_tag(self, context, *tag_args, **tag_kwargs):
        from datetime import datetime
        user = context['user']
        dob = user.dob
        if dob != None:
            return datetime.strftime(dob,'%B %d')
        else:
            return 'Not specified'

@register.simple_tag
def review_rating_ids_names():
    return Review.r

@register.filter
def add_key_val(value,args):
    value[args[:args.find(':')]] = args[args.find(':')+1:]
    return ''

@register.filter
def get_val_length(value,args):
    return 0 if not args in value else len(value[args])


@register.filter
def filter_el(value, args):
    filter = args
    include = {
        'icon':'<i class="icon fa fa-check"></i>',
        'style':'p-primary include'
    }
    exclude = {
        'icon':'<i class="icon fa fa-times"></i>',
        'style':'p-danger-o exclude'
    }
    tmplt = """
    <a class="filter-select col-xs-6 col-sm-4 col-md-6 col-lg-6 pt-1 pr-0">
        <div class="pretty p-icon p-smooth col-12" title="{title}" data-toggle="tooltip">
            <input id="{filter_type}-{id}" class="filter" {filter_meth} type="checkbox" {checked}/>
            <div class="state text-truncate {style}" style="font-size:12px">
                {icon}
                <label>{name}</label>
            </div>
        </div>
    </a>
    """
    # print()
    # print(value)
    # print(args)
    # print()
    tooltip = value['name'] if not 'chosen_tooltip' in value else value[value['chosen_tooltip']]
    null_val = tmplt.format(name=value['name'],title=tooltip,id=value['id'],style='',icon='',filter_type=value['html_id_start'],filter_meth='',checked='')
    if value['op_key'] in filter:
        filter = filter[value['op_key']]
        if ('include' in filter and str(value['id']) in filter['include']) or ('exclude' in filter and str(value['id']) in filter['exclude']):

            if 'include' in filter:
                for inc in filter['include']:
                    # print('>>',inc, str(value['id']), str(value['id']) == inc)
                    if str(value['id']) == inc:
                        tmplt = tmplt.format(name=value['name'],title=tooltip,id=value['id'],style=include['style'],icon=include['icon'],filter_type=value['html_id_start'],filter_meth='data-filter="include"',checked='checked')

            if 'exclude' in filter:
                for exc in filter['exclude']:
                    if str(value['id']) == exc:
                        tmplt = tmplt.format(name=value['name'],title=tooltip,id=value['id'],style=exclude['style'],icon=exclude['icon'],filter_type=value['html_id_start'],filter_meth='data-filter="exclude"',checked='checked')
        else:
            tmplt = null_val
    else:
        tmplt = null_val

    # print(tmplt)
    return tmplt


@register.filter
def shortMonthDateFormat_epoch(e):
    if e == None:
        return None
    from ..apis.helper import epoch_to_date
    m_short = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    d = epoch_to_date(e)
    return '{0} {1}, {2}'.format(m_short[int(d['month'])-1], d['date'],d['year'])

@register.filter
def shortMonthDateFormat_str(s):
    if s == None:
        return None
    # from dateutil.parser import parse
    from datetime import date, datetime
    return datetime.strftime(s.date(), '%b %d, %Y')

@register.filter
def epoch_to_date_str(e):
    from ..apis.helper import epoch_to_date
    d = epoch_to_date(e, str=True)
    return d

@register.filter
def get_game_title_with_year(value):
    from ..apis.helper import epoch_to_date
    year = epoch_to_date(value['first_release_date'])['year']
    return '{0} ({1})'.format(value['name'], year)

@register.filter
def get_game_descr_for_search_r(value):
    descr = value['storyline'] if 'storyline' in value else (value['summary'] if 'summary' in value else '')
    if descr:
        if len(descr) > 214:
            descr = descr[:214] + '...'
    else:
        descr = 'No description available'
    return descr

# @register.simple_tag(takes_context=True)
# def check_if_game_in_list(context, *args, **kwargs):
#     request = context['request']
#     return request.user.gamelistitem_set.filter(game_id=args[0]).exists() if request.user.is_authenticated else False

@register.simple_tag(takes_context=True)
def check_if_game_in_list(context, *args, **kwargs):
    return [i['id'] if i != None else None for i in kwargs['gs']]

@register.simple_tag(takes_context=True)
def ids_recsu(context, *args, **kwargs):
    return [i.similar_game.pk for i in kwargs['gs']]

@register.simple_tag(takes_context=True)
def ids_recsu_all(context, *args, **kwargs):
    r = []
    for i in kwargs['gs']:
        r.append(i.game.pk)
        r.append(i.similar_game.pk)
    return r

@register.simple_tag
def most_popular():
    from django.forms.models import model_to_dict
    g = Game.objects.filter(first_release_date__lt=(datetime.utcnow()).replace(tzinfo=pytz.utc)).order_by('-rating_count')
    g = list(g[:10])
    mp = [{**model_to_dict(i), 'url':i.url, 'title':i.title, 'year':i.year,'rating':i.avg_rating, 'avg_rating_count': pretty_largenumber_commas(i.avg_rating_count)} for i in g]
    # from ..apis.rawg import Rawg
    # return Rawg().most_popular()['results']
    return mp

@register.simple_tag
def latest_reviews():
    from django.forms.models import model_to_dict
    r = Review.objects.filter(timestamp__lt=(datetime.utcnow()).replace(tzinfo=pytz.utc)).order_by('-timestamp')
    r = list(r[:12])
    lr = [{'game_obj':i.game,**model_to_dict(i.game), 'url':i.game.url, 'title':i.game.title,'rating':i.game.avg_rating,'star':float(i.game.avg_rating)*10, 'by':i.user, 'year':i.game.year, 'first_release_date':i.game.first_release_date.timestamp()} for i in r]
    return lr

@register.tag('recs_home')
class recs_home(BaseAssignmentNode):

    def get_value(self, context, *tag_args, **tag_kwargs):
        user = context['request'].user
        r = {}
        def r_g():
            import json
            g_r = GuestRecommendations.objects.all()
            if g_r.exists():
                g_r = g_r[0]
                gs = []
                for i in list(json.loads(g_r.data)):
                    g = Game.objects.filter(id=i)
                    if g.exists():
                        gs.append(g[0])
                return gs
            else:
                return []
        if user.is_authenticated:
            pass
        else:
            pass
        r['guest'] = r_g()
        r['personal'] = list(range(0,10))
        return r

@register.filter
def get_readonly_star_tag(rating):
    return """
    <span class="rating" style="margin-right: 5px;"><span class="fill" style="width:{percent}%"></span></span>
    <span class="p-l-xs score">{value}</span>
    """.format(percent=int(float(rating)*10), value=float(rating))


@register.simple_tag
def top_games():
    from django.forms.models import model_to_dict
    g = Game.objects.filter(first_release_date__lt=(datetime.utcnow()).replace(tzinfo=pytz.utc)).order_by('-rating')
    g = list(g[:5])
    t_g = [{**model_to_dict(i), 'url':i.url, 'title':i.title, 'year':i.year, 'rating':i.avg_rating, 'avg_rating_count': pretty_largenumber_commas(i.avg_rating_count)} for i in g]
    # from ..apis.rawg import Rawg
    # return Rawg().most_popular()['results']
    return t_g

@register.filter
def in_arr(value):
    return value in [6,12,49,9,48,20,37,130,137,160,5,162,165,20,38,46]
