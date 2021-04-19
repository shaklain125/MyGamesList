from datetime import date, datetime
from gamesrec.management.commands.api import ApiMgr
from gamesrec.management.management_helper import GamesUpdateMgr

import gamesrec.management.commands.rec as rec

def projpath(file):
    import os
    from django.conf import settings
    return os.path.join(settings.PROJ_DIR, file)

def curpath(file):
    import os
    cur = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cur, file)

def api_status():
    ApiMgr().clean(log=True, detail=True)

def games_adder():
    if ApiMgr().clean(log=True):
        # GamesUpdateMgr().add_latest_only_if_not_exists_or_update_them('add_update')
        # GamesUpdateMgr().add_latest_only_if_not_exists_or_update_them('add')
        GamesUpdateMgr().add_all_if_not_exists_or_update_all('add')
    print()

def user_ratings_updater():
    rec.update(log=True)

def guest_recs_updater():
    print(f'[{str(datetime.now())}] {rec.update_guest_recs()}')
