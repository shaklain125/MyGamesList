from django.core.management.base import BaseCommand

from gamesrec.models import *
from gamesrec.apis.helper import *
from gamesrec.management.management_helper import *
from gamesrec.apis.igdb import IGDB

import json
import os

from datetime import date, datetime

def curpath(file):
    import os
    cur = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cur, file)

class ApiMgr(object):
    def __init__(self, *args, **kwargs):
        self.igdb = IGDB()

    def add(self, key_val):
        def _add(key):
            q = list(API.objects.filter(key=key))
            if len(q) == 0 and self.check(key):
                a = API(key=key)
                a.save()
                print(a, 'added')
            else:
                if len(q) != 0:
                    print(q,f'\'{key}\'', 'exists')
                else:
                    print(f'\'{key}\'', 'is invalid')
        if key_val == 'file':
            f = open(curpath('api_keys.txt'), 'a+')
            f.seek(0)
            lines = f.readlines()
            f.close()
            for i in lines:
                l = i.rstrip('\n')
                _add(l)
            return
        else:
            _add(key_val)

    def remove(self, key):
        q = list(API.objects.filter(key=key))
        if len(q) != 0 and not self.check(key):
            q[0].delete()
            print(q, 'removed')
        else:
            if len(q) == 0:
                print(q,f'\'{key}\'', 'doesn\'t exist')
            else:
                print(f'\'{key}\'', ' is valid')

    def clean(self, log=False, detail=False):
        apis = list(API.objects.all())
        c = len(apis)
        rm = 0
        for i in range(len(apis)):
            if self.check(apis[i].key) == False:
                apis[i].delete()
                rm += 1
        msg = f'{rm}/{c} keys removed from database'

        curr_key_id = self.get_current_key()
        curr_key_id = curr_key_id.id if curr_key_id != None else None

        if log:
            status = self.status(detail)
            if detail:
                print('***********************************BEGIN********************************************\n')
                print(f'[{str(datetime.now())}]')
                curr = 0
                max = 0
                try:
                    js = status['json'][0]
                    print('   '.join([f'[{k}: {v}]' for k,v in js.items() if k != 'usage_reports']))
                    reps = js['usage_reports']
                    rep = reps['usage_report']
                    max = rep['max_value']
                    curr = rep['current_value']
                    print('   '.join([f'[{k}: {v}]' for k,v in rep.items() if k!= 'max_value' and k!='current_value']))
                except Exception as e:
                    print(f'ERROR printing json response \n{json.dumps(status, indent=2)}')
                status = status['status']
                print(f'[{msg}]   [Working: {status}]   [{curr}/{max}   {max-curr} requests left]   [ID: {curr_key_id}]')
                print('\n***********************************END***********************************************\n')
            else:
                print(f'[{str(datetime.now())}]   {msg}   Working: {status}   ID: {curr_key_id}\n')
            return status
        else:
            print(msg)

        return msg

    def status(self, json=False):
        st = self.igdb.api_status()
        if json:
            return st
        return st['status']

    def get_current_key(self):
        q = list(API.objects.filter(key=self.igdb._headers['user-key']))
        return q[0] if len(q) > 0 else None

    def check(self, key):
        return self.igdb.api_status(key)['status']



class Command(BaseCommand):
    missing_args_message = """
    \nOptions:\n
     clean         ---- Removes invalid keys from database
     status        ---- Checks current api status\n
    -check [key]   ---- Checks api key from database
    -add [key]     ---- Adds api key from database
    -remove [key]  ---- Removes api key from database\n
    """

    def add_arguments(self, parser):
        parser.add_argument('cmd', nargs='?')
        parser.add_argument('-check', nargs='?', help='checks api keys')
        parser.add_argument('-add', nargs='?', help='adds an api key')
        parser.add_argument('-remove', nargs='?', help='removes an api key')

    def handle(self, *args, **options):
        apimgr = ApiMgr()
        if options['cmd'] == 'status':
            st = apimgr.status()
            print(st)
            return
        elif options['cmd'] == 'clean':
            apimgr.clean()
            return
        if options['check']:
            print(apimgr.check(options['check']), options['check'])
            return
        elif options['add']:
            apimgr.add(options['add'])
        elif options['remove']:
            apimgr.remove(options['remove'])
            return
