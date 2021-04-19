"""gamesproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, re_path, include, reverse,reverse_lazy
from django.contrib.auth import views as auth_views
from . import views
from .forms import LoginForm
from gamesrec.models import *
from django.template.defaultfilters import slugify

app_name = 'gamesrec'

status_names_slugs = '|'.join([slugify(i.lower()) for i in GameListItem.status_names])

game_tabs = '|'.join([slugify(i.lower()) for i in ['reviews','add_rec','write_review','photos','recs','statistics']])

def extra_email_context():
    return {
        'host':'example.net'
    }

urlpatterns = [
    path('',views.index,name='index'),

    path('signin/',views.signin,name='login'),
    path('signup/',views.register,name='register'),

    path('logout/',views.logout,name='logout'),

    # path('profile',views.profile,name='profile_auto'),
    # path('profile/<str:username>',views.profile,name='profile'),
    re_path(r'^profile/$',views.profile,name='profile_null'),
    re_path(r'^profile/(?P<username>.*)/$',views.profile,name='profile'),
    re_path(r'^profile/(?P<username>.*)/(?P<profile_tab>stats|recs|reviews|history)$',views.profile,name='profile_tab'),
    re_path(r'^profile/(?P<username>.*)/(?P<profile_tab>edit_review|edit_rec)/(?P<id>\d+)$',views.profile,name='profile_tab_sub'),
    re_path(r'^profile/(?P<username>.*)/remove_review$',views.remove_review,name='remove_review'),
    re_path(r'^profile/(?P<username>.*)/remove_rec$',views.remove_rec,name='remove_rec'),

    path('recommendations',views.recent_recommendations, name='recent_recommendations'),
    path('recommendations/',views.recent_recommendations, name='recent_recommendations1'),

    path('comments_test',views.comments_test, name='comments_test'),
    path('comment',views.comment, name='comment'),
    path('reply',views.reply, name='reply'),
    path('load_comments', views.load_comments, name='load_comments'),
    path('load_replies', views.load_replies, name='load_replies'),
    path('editable', views.get_comment_txtarea, name='get_comment_txtarea'),
    path('update_comment', views.update_comment, name='update_comment'),
    path('get_replies_count_msg', views.get_replies_count_msg, name='get_replies_count_msg'),
    path('comment_rate', views.comment_rate, name='comment_rate'),
    path('get_comments_count', views.get_comments_count, name='get_comments_count'),

    path('darkmode/toggle',views.darkmode_toggle,name='darkmode_toggle'),

    path('account/profile/',views.account_settings,name='account_settings'),
    path('account/privacy/',views.account_settings,name='account_privacy'),
    path('upload/picture/',views.upload_picture, name='upload_picture'),
    path('remove/picture/',views.remove_picture, name='remove_picture'),
    path('last_online/user', views.last_online, name='last_online'),

    re_path(r'^gameslist/(?P<username>.*)/$', views.gameslist, name='gameslist'),
    re_path(r'^gameslist/(?P<username>.*)/(?P<list_type>'+status_names_slugs+')$', views.gameslist, name='gameslist'),
    path('lists/games/',views.get_games_lists, name='get_games_lists'),
    path('lists/games/count/',views.get_lists_count, name='get_lists_count'),

    path('personal_recs/',views.get_personal_recs, name='get_personal_recs'),

    path('latest/',views.get_latest, name='get_latest'),

    path('404/',views.handler404, name='404'),
    path('500/',views.handler500, name='500'),
    re_path(r'^api/(?P<key>.*)$',views.check_api_status, name='check_api_status'),

    path('search',views.search, name='search'),
    path('search/',views.search, name='search1'),
    path('autocomplete/query',views.search_autocomplete, name='search_autocomplete'),
    path('add_or_edit_bool', views.add_or_edit_bool, name='add_or_edit_bool'),

    re_path(r'^(?P<igdb_id>\d+)-(?P<slug>[\w-]+)/(?P<tab_name>'+game_tabs+')$',views.game, name='game_tab'),
    re_path(r'^(?P<igdb_id>\d+)-(?P<slug>[\w-]+)/(?P<tab_name>'+game_tabs+')/$',views.game, name='game_tab1'),
    path('<int:igdb_id>-<slug:slug>/',views.game, name='game'),

    path('reviews/helpful',views.review_helpful, name='review_helpful'),
    path('recs/like',views.recs_like, name='recs_like'),

    path('g_data/',views.get_game_d, name='get_game_d'),
    path('user/rating', views.get_your_rating, name='get_your_rating'),
    path('stats/',views.get_game_stats, name='get_game_stats'),

    path('find_friends/',views.find_friends, name='find_friends'),
    path('search_friends/',views.search_friends, name='search_friends'),

    path('user/list/action',views.list_action, name='list_action'),
    path('user/list/ratings/history',views.list_item_rating_history, name='list_item_rating_history'),

    path('atl/form',views.atl_edit_form, name='atl_edit_form'),

    path('user/list/updates',views.recent_list_updates,name='recent_list_updates'),


    path('letter/<str:name>',views.letter, name='letter'),
    path('letter/<str:name>/<int:size>',views.letter, name='letter_size'),

    path('games/stores/',views.stores_of_game, name='stores_of_game'),

    path('igdb/game/',views.get_igdb_game, name='get_igdb_game'),
    path('rawg/game/',views.get_rawg_game, name='get_rawg_game'),
    path('igdb/trailers',views.get_igdb_trailers, name='get_igdb_trailers'),

    path('genres-themes/',views.get_genres_and_themes, name='get_genres_and_themes'),

    path('logged_in_devices/',views.get_user_sessions, name='get_user_sessions'),
    path('remove_device/',views.remove_session, name='remove_session'),

    path('analytics',views.analytics, name='analytics'),
    path('analytics/',views.analytics, name='analytics1'),
    path('user_actions/',views.get_user_actions, name='get_user_actions'),

    path('load_history/',views.load_history, name='load_history'),

    path('log_search_query/', views.log_search_query, name='log_search_query'),
    path('get_popular_searches/', views.get_popular_searches, name='get_popular_searches'),

    path('log_friends_search_query/', views.log_friends_search_query, name='log_friends_search_query'),

    path('export/list', views.export_list, name='export_list'),




    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='gamesrec/account/password_reset.html',
        email_template_name='gamesrec/account/password_reset_email.html',
        html_email_template_name='gamesrec/account/password_reset_email.html',
        subject_template_name='gamesrec/account/password_reset_subject.html',
        extra_email_context= extra_email_context(),
        success_url=reverse_lazy('gamesrec:password_reset_done')
        ),
        name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='gamesrec/account/password_reset_done.html'
        ),
        name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='gamesrec/account/password_reset_confirm.html',
        success_url=reverse_lazy('gamesrec:password_reset_complete')
        ),
        name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='gamesrec/account/password_reset_complete.html'
        ),
        name='password_reset_complete'),

    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='gamesrec/account/password_change.html',
        success_url=reverse_lazy('gamesrec:password_change_done'),
        ),
        name='password_change'),

    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='gamesrec/account/password_change_done.html'
        ),
        name='password_change_done'),

    path('registation-complete',views.registration_complete, name='registration_complete'),

    path('_test_html',views._test_html, name='_test_html'),
]
