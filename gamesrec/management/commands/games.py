from django.core.management.base import BaseCommand

from gamesrec.models import *
from gamesrec.apis.helper import *
from gamesrec.management.management_helper import *

import json

class Command(BaseCommand):
    missing_args_message = """
    \nOptions:\n
    add           ---- Adds new games in the database with IGDB and Rawg values
    update        ---- Updates all games in the database with IGDB and Rawg values
    addlatest     ---- Adds latest new games in the database with IGDB and Rawg values
    updatelatest  ---- Update latest new games in the database with IGDB and Rawg values
    count         ---- Counts all games in IGDB database\n
    """
    def add_arguments(self, parser):
        parser.add_argument('cmd', choices=['update', 'add','add_update' ,'addlatest', 'updatelatest','add_update_latest','count','update_details'])

    def handle(self, *args, **options):
        mgr = GamesUpdateMgr()
        if options['cmd'] == 'add':
            mgr.add_all_if_not_exists_or_update_all(option='add')
        elif options['cmd'] == 'update':
            mgr.add_all_if_not_exists_or_update_all(option='update')
        elif options['cmd'] == 'add_update':
            mgr.add_all_if_not_exists_or_update_all(option='add_update')
        elif options['cmd'] == 'count':
            mgr.add_all_if_not_exists_or_update_all(option='count')
        elif options['cmd'] == 'update_details':
            mgr.update_games()

        elif options['cmd'] == 'addlatest':
            mgr.add_latest_only_if_not_exists_or_update_them(option='add')
        elif options['cmd'] == 'updatelatest':
            mgr.add_latest_only_if_not_exists_or_update_them(option='update')
        elif options['cmd'] == 'add_update_latest':
            mgr.add_latest_only_if_not_exists_or_update_them(option='add_update')
