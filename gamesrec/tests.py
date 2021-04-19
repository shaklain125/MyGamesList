from django.test import TestCase, Client
from django.urls import path, include, reverse, resolve
from gamesrec.models import *
from gamesrec.views import *

class UserTestCase(TestCase):
    #Testing URLS
    def test_urls(self):
        url = reverse('gamesrec:index')
        self.assertEqual(resolve(url).func, index)
        self.assertEqual(resolve(url).url_name, "index")

        url = reverse('gamesrec:login')
        self.assertEqual(resolve(url).func, signin)
        self.assertEqual(resolve(url).url_name, "login")

        url = reverse('gamesrec:register')
        self.assertEqual(resolve(url).func, register)
        self.assertEqual(resolve(url).url_name, "register")

        url = reverse('gamesrec:logout')
        self.assertEqual(resolve(url).func, logout)
        self.assertEqual(resolve(url).url_name, "logout")


        url = reverse('gamesrec:profile_null')
        self.assertEqual(resolve(url).func, profile)
        self.assertEqual(resolve(url).url_name, "profile_null")

        # url = reverse('gamesrec:profile')
        # self.assertEqual(resolve(url).func, profile)
        # self.assertEqual(resolve(url).url_name, "profile")
        #
        # url = reverse('gamesrec:profile_tab')
        # self.assertEqual(resolve(url).func, profile)
        # self.assertEqual(resolve(url).url_name, "profile_tab")
        #
        # url = reverse('gamesrec:profile_tab_sub')
        # self.assertEqual(resolve(url).func, profile)
        # self.assertEqual(resolve(url).url_name, "profile_tab_sub")
        #
        # url = reverse('gamesrec:remove_review')
        # self.assertEqual(resolve(url).func, remove_review)
        # self.assertEqual(resolve(url).url_name, "remove_review")

        url = reverse('gamesrec:account_settings')
        self.assertEqual(resolve(url).func, account_settings)
        self.assertEqual(resolve(url).url_name, "account_settings")


        url = reverse('gamesrec:upload_picture')
        self.assertEqual(resolve(url).func, upload_picture)
        self.assertEqual(resolve(url).url_name, "upload_picture")

        url = reverse('gamesrec:remove_picture')
        self.assertEqual(resolve(url).func, remove_picture)
        self.assertEqual(resolve(url).url_name, "remove_picture")

        url = reverse('gamesrec:last_online')
        self.assertEqual(resolve(url).func, last_online)
        self.assertEqual(resolve(url).url_name, "last_online")

        # url = reverse('gamesrec:gameslist')
        # self.assertEqual(resolve(url).func, gameslist)
        # self.assertEqual(resolve(url).url_name, "gameslist")
        #
        # url = reverse('gamesrec:get_games_lists')
        # self.assertEqual(resolve(url).func, get_games_lists)
        # self.assertEqual(resolve(url).url_name, "get_games_lists")

        url = reverse('gamesrec:get_lists_count')
        self.assertEqual(resolve(url).func, get_lists_count)
        self.assertEqual(resolve(url).url_name, "get_lists_count")

        url = reverse('gamesrec:get_personal_recs')
        self.assertEqual(resolve(url).func, get_personal_recs)
        self.assertEqual(resolve(url).url_name, "get_personal_recs")

        url = reverse('gamesrec:get_latest')
        self.assertEqual(resolve(url).func, get_latest)
        self.assertEqual(resolve(url).url_name, "get_latest")

        url = reverse('gamesrec:404')
        self.assertEqual(resolve(url).func, handler404)
        self.assertEqual(resolve(url).url_name, "404")

        url = reverse('gamesrec:500')
        self.assertEqual(resolve(url).func, handler500)
        self.assertEqual(resolve(url).url_name, "500")

        # url = reverse('gamesrec:check_api_status')
        # self.assertEqual(resolve(url).func, check_api_status)
        # self.assertEqual(resolve(url).url_name, "check_api_status")

        url = reverse('gamesrec:search')
        self.assertEqual(resolve(url).func, search)
        self.assertEqual(resolve(url).url_name, "search")

        url = reverse('gamesrec:search_autocomplete')
        self.assertEqual(resolve(url).func, search_autocomplete)
        self.assertEqual(resolve(url).url_name, "search_autocomplete")

        url = reverse('gamesrec:add_or_edit_bool')
        self.assertEqual(resolve(url).func, add_or_edit_bool)
        self.assertEqual(resolve(url).url_name, "add_or_edit_bool")

        # url = reverse('gamesrec:game_tab')
        # self.assertEqual(resolve(url).func, game)
        # self.assertEqual(resolve(url).url_name, "game_tab")

        # url = reverse('gamesrec:game')
        # self.assertEqual(resolve(url).func, game)
        # self.assertEqual(resolve(url).url_name, "game")

        url = reverse('gamesrec:review_helpful')
        self.assertEqual(resolve(url).func, review_helpful)
        self.assertEqual(resolve(url).url_name, "review_helpful")

        url = reverse('gamesrec:get_game_d')
        self.assertEqual(resolve(url).func, get_game_d)
        self.assertEqual(resolve(url).url_name, "get_game_d")

        url = reverse('gamesrec:get_your_rating')
        self.assertEqual(resolve(url).func, get_your_rating)
        self.assertEqual(resolve(url).url_name, "get_your_rating")

        url = reverse('gamesrec:list_action')
        self.assertEqual(resolve(url).func, list_action)
        self.assertEqual(resolve(url).url_name, "list_action")

        url = reverse('gamesrec:list_item_rating_history')
        self.assertEqual(resolve(url).func, list_item_rating_history)
        self.assertEqual(resolve(url).url_name, "list_item_rating_history")

        url = reverse('gamesrec:atl_edit_form')
        self.assertEqual(resolve(url).func, atl_edit_form)
        self.assertEqual(resolve(url).url_name, "atl_edit_form")

        url = reverse('gamesrec:recent_list_updates')
        self.assertEqual(resolve(url).func, recent_list_updates)
        self.assertEqual(resolve(url).url_name, "recent_list_updates")

        # url = reverse('gamesrec:letter')
        # self.assertEqual(resolve(url).func, letter)
        # self.assertEqual(resolve(url).url_name, "letter")
        #
        # url = reverse('gamesrec:letter_size')
        # self.assertEqual(resolve(url).func, letter)
        # self.assertEqual(resolve(url).url_name, "letter_size")

        url = reverse('gamesrec:get_genres_and_themes')
        self.assertEqual(resolve(url).func, get_genres_and_themes)
        self.assertEqual(resolve(url).url_name, "get_genres_and_themes")

    #Testing Views
    def test_Views(self):
        client = Client()

        response = client.get(reverse('gamesrec:index'))
        self.assertEqual(response.status_code, 200)
        # self.assertTemplateUsed(response, "gamesrec/base.html")
