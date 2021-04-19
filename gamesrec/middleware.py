from django.urls import resolve
from django.utils import timezone
from gamesrec.models import *
from django.db.models import Q, Count
from gamesrec.apis.session_info import *
from django.conf import settings

class user_session_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'GET':
            # print('user_session_middleware--------------------------------------', resolve(request.path_info).url_name)
            [i.expire() for i in UserSession.objects.all()]
            u_s = UserSession.objects.filter(session_key=request.session.session_key)
            if u_s.exists():
                u_s = u_s[0]
                u_s.update_active()
                u_s.expire()
        response = self.get_response(request)
        return response


class analytics_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user_action_path_names = [
            'login', 'register', 'game_tab', 'game_tab1', 'game', 'profile_tab',
            'remove_review','remove_rec', 'comment', 'reply','update_comment','comment_rate',
            'darkmode_toggle','account_settings','account_privacy','upload_picture','remove_picture',
            'search','search1','search_autocomplete','review_helpful', 'recs_like','search_friends',
            'list_action','remove_session',
        ]
        path_name = resolve(request.path_info).url_name
        if request.method == 'POST':
            if path_name in user_action_path_names:
                if request.user.is_authenticated:
                    ua = UserAction(action_name=path_name,**get_user_info_log(request))
                    ua.save()
                    # print('USER ACTION LOG: --------------------------------------------->', path_name)
        r2 = request.user
        r = request
        if not request.user.is_authenticated:
            r.user = None
        if request.method == 'GET':
            u_log = UsageLog(**get_user_info_log(r))
            u_log.save()
        request.user = r2
        response = self.get_response(request)
        return response

class theme_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        def get_reg_user_dark_mode():
            user = request.user
            try:
                if user.is_authenticated and user.profile.dark_mode:
                    return True
                else:
                    return False
            except Exception as e:
                return False
        request.dark_mode = get_reg_user_dark_mode()
        if not request.user.is_authenticated:
            if 'dark_mode' in request.COOKIES:
                request.dark_mode = request.COOKIES['dark_mode'] == '1'
        response = self.get_response(request)
        return response

from .apis.igdb import IGDB

class api_status_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        exclude = ['logout', 'letter', 'letter_size', 'darkmode_toggle']
        path_name = resolve(request.path_info).url_name
        is_media = request.path_info.startswith(settings.MEDIA_URL)
        if request.method == 'GET' and (not path_name in exclude) and (not is_media):
            if not (API.objects.all().exists() and IGDB().check_key()):
                return render(request, 'gamesrec/error_pages/500.html',{'api': 'Api usage limit reached'})

        response = self.get_response(request)
        return response
