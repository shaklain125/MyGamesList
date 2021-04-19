from datetime import date
from collections import defaultdict
import requests

# f = open(curpath('api_status.txt'), 'a+')
# f.writelines('')
# f.close()

def epoch_to_date(e, str=False):
    import time
    try:
        e = int(e)
        d = time.strftime('%Y-%m-%d', time.localtime(e))
        if str:
            return d
        d_s = d.split('-')
        return {
            'date': d_s[2],
            'month': d_s[1],
            'year': d_s[0]
        }
    except Exception as e:
        return None

def getAge(dob):
    from datetime import date
    today = date.today()
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    return age

def pretty_large_short(n):
    # mgn = 0
    # while abs(n) >= 1000:
    #     mgn += 1
    #     n /= 1000.0
    # return '%.2f%s' % (num, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])
    try:
        if n < 10:
            return n
        from millify import millify
        return millify(n,precision=2).upper()
    except Exception as e:
        return n

def pretty_largenumber_commas(s):
    import re
    return re.sub('\B(?=(\d{3})+(?!\d))',',',str(s))

def get_title(val, r='_'):
    return val.replace(r,' ').title()

def parseInt(val):
    try:
        int(val)
        return int(val)
    except ValueError:
        return None

def epoch_to_dateUTC(e):
    from datetime import datetime
    import pytz
    try:
        e = datetime.fromtimestamp(int(e))
        e = e.replace(tzinfo=pytz.UTC)
        return e
    except Exception as e:
        return None

def century_dt(epoch=False):
    from datetime import datetime,date
    c_year = (date.today().year) - ((date.today().year) % 100)
    c = '{c_year}-01-01'.format(c_year=c_year)
    c = datetime.strptime(c,'%Y-%m-%d')
    if epoch:
        return int(c.timestamp())
    else:
        return c


def get_steam_release_date(i):
    def steam_released_date(link):
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
    try:
        ws = [w for w in i['websites'] if 'steam' in w['url'].lower()]
        ws = (ws[0]['url'] if 'url' in ws[0] else None) if len(ws) > 0 else None
        if ws != None:
            rel = steam_released_date(ws)
            if rel == None:
                return None
            else:
                return rel
        else:
            return None
    except Exception as e:
        return None

def sameln(s):
    import sys
    sys.stdout.write(f'\r{s}')
    sys.stdout.write("\033[K")


def get_steam(i):
    def steam_data(link):
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
            d = d[str(id)]['data']
            return d
        except Exception as e:
            print(e)
            return None
    try:
        ws = [w for w in i['websites'] if 'steam' in w['url'].lower()]
        ws = (ws[0]['url'] if 'url' in ws[0] else None) if len(ws) > 0 else None
        return steam_data(ws) if ws != None else None
    except Exception as e:
        return None


def year_dt(year, epoch=False):
    from datetime import datetime,date
    c = '{year}-01-01'.format(year=year)
    c = datetime.strptime(c,'%Y-%m-%d')
    return str(int(c.timestamp())) if epoch else c

def str_dt_timestamp(dt, epoch=False):
    from datetime import datetime,date
    c = datetime.strptime(dt,'%Y-%m-%d')
    return str(int(c.timestamp()))

def end_year_dt(year, epoch=False):
    from datetime import datetime,date
    c = '{year}-12-31'.format(year=year)
    c = datetime.strptime(c,'%Y-%m-%d')
    return str(int(c.timestamp())) if epoch else c

def intToRoman(num):
    try:
        num = int(num)
    except Exception as e:
        return False
    val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    syb = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    roman_num = ''
    i = 0
    while  num > 0:
        for _ in range(num // val[i]):
            roman_num += syb[i]
            num -= val[i]
        i += 1
    return roman_num.lower()

def count_same_items(a,b):
    count = 0
    for j in range(len(a)):
        for i in range(len(b)):
            if a[j] == b[i]:
                count += 1
                break
    return count

def merge(shared_key, *iterables):
    result = defaultdict(dict)
    for dictionary in itertools.chain.from_iterable(iterables):
        result[dictionary[shared_key]].update(dictionary)

    for dictionary in result.values():
        dictionary.pop(shared_key)
    return result

def encryption(val, encrypt=True, get_bytes=False):
    from cryptography.fernet import Fernet
    key = b'H_Vnv-Roe3ESJjFlZAOikapWt1oAQYEn_XGlHB4jasI=' #Fernet.generate_key()
    f = Fernet(key)
    val = str(val)
    if encrypt:
        encoded = f.encrypt(val.encode())
        return encoded if get_bytes else encoded.decode('utf8').replace("'", '"')
    else:
        try:
            decrypted = f.decrypt(val.encode())
            return decrypted.decode()
        except Exception as e:
            return None

#rawg

def century_year():
    y = date.today().year
    return y - (y % 100)

def similar(a, b):
    from difflib import SequenceMatcher
    return SequenceMatcher(None, a, b).ratio()

def romanToInt(s):
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val[s[i]]
    return int_val

def checkIfRomanNumeral(numeral):
    numeral = str(numeral)
    numeral = numeral.upper()
    validRomanNumerals = ["M", "D", "C", "L", "X", "V", "I"]
    for letters in numeral:
        if letters not in validRomanNumerals:
            return False
    return romanToInt(numeral)

def get_timestamp(dt):
    from datetime import date, datetime
    current = datetime.now()
    previous = dt.replace(tzinfo=None)
    msPerMinute = 60 * 1000
    msPerHour = msPerMinute * 60
    msPerDay = msPerHour * 24
    msPerMonth = msPerDay * 30
    msPerYear = msPerDay * 365

    elapsed = (current - previous).total_seconds()*1000
    # elapsed = 365*30*elapsed.days * 24 * 3600 + elapsed.seconds* 1000
    # print('')
    # print(('{0} - {1}').format(current,previous))
    # print(elapsed)
    # print('')
    def str_t(t_n, val):
        if int(val) == 1:
            return '{0} {1} ago'.format(val, t_n)
        else:
            return '{0} {1}s ago'.format(val, t_n)
    if (elapsed < msPerMinute):
        return str_t('second', round(elapsed/1000))
    elif (elapsed < msPerHour):
        return str_t('minute', round(elapsed/msPerMinute))
    elif (elapsed < msPerDay ):
        return str_t('hour', round(elapsed/msPerHour))
    elif (elapsed < msPerMonth):
        return str_t('day', round(elapsed/msPerDay))
    elif (elapsed < msPerYear):
        return str_t('month', round(elapsed/msPerMonth))
    else:
        return str_t('year', round(elapsed/msPerYear))


def pretty_dt_timestamp(time=False, format=None):
    from datetime import datetime
    import pytz

    def get_format():
        if format != None:
            return format
        formats = ['%Y-%m-%d %H:%M:%S.%f %z','%Y-%m-%d %H:%M:%S.%f','%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d']
        for i in formats:
            try:
                t = time if type(time) == str else str(time.strftime(i))
                d = datetime.strptime(t,i)
                return i
            except Exception as e:
                continue
        return None
    now = datetime.utcnow().replace(tzinfo=pytz.utc) #datetime.now()
    if type(time) is int or type(time) is float or type(time) is str:
        if type(time) is int or type(time) is float:
            time = datetime.fromtimestamp(time)
        else:
            format = get_format()
            if format == None:
                return None
            time = datetime.strptime(time,format)
        time = time.replace(tzinfo=pytz.utc)
        diff = now - time
    elif isinstance(time,datetime) or isinstance(time,date):
        format = get_format()
        if format == None:
            return None
        time = str(time.strftime(format))
        time = datetime.strptime(time,format)
        time = time.replace(tzinfo=pytz.utc)
        diff = now - time
    elif not time:
        diff = now - now
    else:
        return None
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    def str_t(diff, t, name):
        def sing_plu(val, t_n):
            if int(val) == 1:
                return '{0} {1} ago'.format(val, t_n)
            else:
                return '{0} {1}s ago'.format(val, t_n)
        return sing_plu(round(diff / t),name)

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str_t(diff=second_diff, t=1, name='second')
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str_t(diff=second_diff, t=60, name='minute')
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str_t(diff=second_diff, t=3600, name='hour')
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str_t(diff=day_diff, t=1, name='day')
    if day_diff < 31:
        return str_t(diff=day_diff, t=7, name='week')
    if day_diff < 365:
        return str_t(diff=day_diff, t=30, name='month')
    else:
        return str_t(diff=day_diff, t=365, name='year')



class SearchFilterMgr(object):

    def get_filters2(self,q):
        from datetime import datetime,date
        from gamesrec.models import Platform, GameMode, Perspective, Game, Genre, Theme, AgeRating
        from django.db.models import Q
        import numpy as np
        fi = {}
        fi2 = {}
        u = {
            'pl':'platforms',
            'gm':'game_modes',
            'pp':'player_perspectives',
            'ge':'genres',
            'th':'themes',
            'ar_p':'age_ratings.category_p',
            'ar_e':'age_ratings.category_e',
        }
        u_db = {
            'platforms':'platforms__pk',
            'game_modes':'game_modes__pk',
            'player_perspectives':'player_perspectives__pk',
            'genres':'genres__pk',
            'themes':'themes__pk',
            'age_ratings.category_p': 'age_ratings__rating',
            'age_ratings.category_e':'age_ratings__rating',
        }
        u2 = {
            're':'released',
            'so':'sort'
        }
        sort_options = [
            'Relevance',
            {'Most popular':'; sort popularity desc'},
            {'Newest':'& first_release_date <= {now}; sort first_release_date desc'},
            {'Released date':';sort first_release_date asc'},
            {'Top rated':' & rating >= 0; sort rating desc'},
            # {'Top ranked':''}
        ]
        sort_options_db = [
            'Relevance',
            {'Most popular':'-popularity'},
            {'Newest':{'q_obj':Q(first_release_date__lte=epoch_to_dateUTC(int(str(int(datetime.now().timestamp()))))),'val':'-first_release_date'}},
            {'Released date':'first_release_date'},
            {'Top rated':{'q_obj':Q(rating_count__gte=0),'val':'-rating'}},
            # {'Top ranked':''}
        ]

        for i in q.keys():
            if i in u2:
                if i == 're':
                    val = q.get(i).split(',')
                    # print('BEFORE:>>>>',val,val[0], val[1])
                    min_y = 1980 #(date.today().year) - ((date.today().year) % 100)
                    val[0] = min_y if int(val[0]) < min_y else int(val[0])
                    val[1] = date.today().year+10 if int(val[1]) > date.today().year+10 else int(val[1])
                    # print(val,val[0], val[1])
                    cr = '(first_release_date >= {0} & first_release_date <= {1})'.format(year_dt(val[0],True),end_year_dt(val[1],True))
                    fi2['released'] = {'created':cr,'json':{'released':{'from':val[0],'to':val[1]}}, 'db':Q(first_release_date__gte=epoch_to_dateUTC(year_dt(val[0],True)))&Q(first_release_date__lte=epoch_to_dateUTC(end_year_dt(val[1],True))),}
                elif i == 'so':
                    s_opt = parseInt(q.get(i))
                    if s_opt != None:
                        s_opt = s_opt-1
                        if s_opt > 0 and s_opt < len(sort_options):
                            option = sort_options[s_opt]
                            cr = next(iter(option.values()))
                            db = next(iter(sort_options_db[s_opt].values()))
                            if s_opt == 2:
                                cr = cr.format(now=str(int(datetime.now().timestamp())))
                            if len(cr.strip()) != 0:
                                fi2['sort'] = {'created':cr,'json':{'sort':s_opt+1},'db':db}
            if i in u:
                val = q.get(i).split(',')
                for j in val:
                    if j.startswith('-'):
                        if u[i] in fi:
                            if 'exclude' in fi[u[i]]:
                                fi[u[i]]['exclude'].append(j[1:])
                            else:
                                fi[u[i]]['exclude'] = [j[1:]]
                        else:
                            fi[u[i]] = {'exclude':[]}
                            fi[u[i]]['exclude'] = [j[1:]]
                    else:
                        if u[i] in fi:
                            if 'include' in fi[u[i]]:
                                fi[u[i]]['include'].append(j)
                            else:
                                fi[u[i]]['include'] = [j]
                        else:
                            fi[u[i]] = {'include':[]}
                            fi[u[i]]['include'] = [j]
        filters = []
        filters_db = []
        if 'released' in fi2:
            filters.append(fi2['released']['created'])
            filters_db.append(fi2['released']['db'])

        for k in fi.keys():
            fi[k]['key'] = k
            if k.startswith('age_ratings.category'):
                q = np.bitwise_or.reduce([Q(**{u_db[k]:int(j)}) for j in fi[k]['include']]) if 'include' in fi[k] else None
                q2 = np.bitwise_and.reduce([~Q(**{u_db[k]:int(j)}) for j in fi[k]['exclude']]) if 'exclude' in fi[k] else None
                if q != None and q2 != None:
                    q = q & q2
                else:
                    if q == None:
                        q = q2
                filters_db.append(q)
                filters.append(self.create_filter_single_val_p_e(k,fi[k]))
            else:
                q = [Q(**{u_db[k]:int(j)}) for j in fi[k]['include']] if 'include' in fi[k] else None
                q2 = [~Q(**{u_db[k]:int(j)}) for j in fi[k]['exclude']] if 'exclude' in fi[k] else None
                if q != None and q2 != None:
                    q = q + q2
                else:
                    if q == None:
                        q = q2
                filters_db += q
                filters.append(self.create_filter(k,fi[k]))
        if 'released' in fi2:
            fi.update(fi2['released']['json'])
        if 'sort' in fi2:
            fi.update(fi2['sort']['json'])
        return {'json':fi,'created':' & '.join(filters),'filters_db':filters_db, 'sort': fi2['sort']['created'] if 'sort' in fi2 else None, 'sort_db': fi2['sort']['db'] if 'sort' in fi2 else None}

    def get_filters(self,q):
        fi = {}
        fi2 = {}
        u = {
            'pl':'platforms',
            'gm':'game_modes',
            'pp':'player_perspectives',
            'ge':'genres',
            'th':'themes',
            'ar_p':'age_ratings.category_p',
            'ar_e':'age_ratings.category_e',
        }
        u2 = {
            're':'released',
            'so':'sort'
        }
        sort_options = [
            'Relevance',
            {'Most popular':'; sort popularity desc'},
            {'Newest':'& first_release_date <= {now}; sort first_release_date desc'},
            {'Released date':';sort first_release_date asc'},
            {'Top rated':' & rating >= 0; sort rating desc'},
            # {'Top ranked':''}
        ]
        from datetime import datetime,date
        for i in q.keys():
            if i in u2:
                if i == 're':
                    val = q.get(i).split(',')
                    # print('BEFORE:>>>>',val,val[0], val[1])
                    min_y = 1980 #(date.today().year) - ((date.today().year) % 100)
                    val[0] = min_y if int(val[0]) < min_y else int(val[0])
                    val[1] = date.today().year+10 if int(val[1]) > date.today().year+10 else int(val[1])
                    # print(val,val[0], val[1])
                    cr = '(first_release_date >= {0} & first_release_date <= {1})'.format(year_dt(val[0],True),end_year_dt(val[1],True))
                    fi2['released'] = {'created':cr,'json':{'released':{'from':val[0],'to':val[1]}}}
                elif i == 'so':
                    s_opt = parseInt(q.get(i))
                    if s_opt != None:
                        s_opt = s_opt-1
                        if s_opt > 0 and s_opt < len(sort_options):
                            option = sort_options[s_opt]
                            cr = next(iter(option.values()))
                            if s_opt == 2:
                                cr = cr.format(now=str(int(datetime.now().timestamp())))
                            if len(cr.strip()) != 0:
                                fi2['sort'] = {'created':cr,'json':{'sort':s_opt+1}}
            if i in u:
                val = q.get(i).split(',')
                for j in val:
                    if j.startswith('-'):
                        if u[i] in fi:
                            if 'exclude' in fi[u[i]]:
                                fi[u[i]]['exclude'].append(j[1:])
                            else:
                                fi[u[i]]['exclude'] = [j[1:]]
                        else:
                            fi[u[i]] = {'exclude':[]}
                            fi[u[i]]['exclude'] = [j[1:]]
                    else:
                        if u[i] in fi:
                            if 'include' in fi[u[i]]:
                                fi[u[i]]['include'].append(j)
                            else:
                                fi[u[i]]['include'] = [j]
                        else:
                            fi[u[i]] = {'include':[]}
                            fi[u[i]]['include'] = [j]
        filters = []
        if 'released' in fi2:
            filters.append(fi2['released']['created'])
        for k in fi.keys():
            fi[k]['key'] = k
            if k.startswith('age_ratings.category'):
                filters.append(self.create_filter_single_val_p_e(k,fi[k]))
            else:
                filters.append(self.create_filter(k,fi[k]))
        if 'released' in fi2:
            fi.update(fi2['released']['json'])
        if 'sort' in fi2:
            fi.update(fi2['sort']['json'])
        return {'json':fi,'created':' & '.join(filters), 'sort': fi2['sort']['created'] if 'sort' in fi2 else None}

    def create_filter(self,key, filter):
        include = '{key}=[{values}]'.format(key=key,values=','.join([str(v) for v in filter['include']])) if 'include' in filter else None
        exclude = '{key}!=[{values}]'.format(key=key,values=','.join([str(v) for v in filter['exclude']])) if 'exclude' in filter else None
        if include != None and exclude != None:
            return ' & '.join([include,exclude])
        else:
            if include != None:
                return include
            else:
                return exclude

    def create_filter_single_val_p_e(self,key, filter):
        categ = key[key.rfind('_')+1:]
        categ = 1 if categ == 'e' else 2
        include = '(age_ratings.rating=({0}))'.format(','.join([str(v) for v in filter['include']])) if 'include' in filter else None
        exclude = '(age_ratings.rating!=({0}))'.format(','.join([str(v) for v in filter['exclude']])) if 'exclude' in filter else None
        if include != None and exclude != None:
            return ' & '.join([include,exclude])
        else:
            if include != None:
                return include
            else:
                return exclude
