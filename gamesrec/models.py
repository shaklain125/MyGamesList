import os, time, uuid
from django.conf import settings
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils import timezone
from django.urls import reverse
import datetime
from jsonfield import JSONField
from unixtimestampfield.fields import UnixTimeStampField
from django.db.models import Q
import numpy as np
from django.shortcuts import render, redirect, reverse
from django.template.defaultfilters import slugify


# Create your models here.
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        uid = uuid.uuid4().hex[:20]    #eg: '567ae32f97e32e32f97f97'

        # eg: 'my-uploaded-file'
        # new_name = '-'.join(filename.replace('.%s' % ext, '').split())

        renamed_filename = '{0}.{1}'.format(uid,ext) # '{0}_{1}.{2}'.format(new_name,uid,ext)
        return  os.path.join(self.path, renamed_filename)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class GeneralUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False) # a admin user; non super-user
    is_admin = models.BooleanField(default=False) # a superuser
    # notice the absence of a "Password field", that's built in.

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    class Meta:
        abstract = True

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

class User(GeneralUser):
    username = models.CharField(max_length=64, unique=True, blank=True, null=True)
    joined = models.DateTimeField(auto_now_add=True)
    # first_name = models.CharField(max_length=50, blank=True, null=True)
    # last_name = models.CharField(max_length=50, blank=True,  null=True)
    dob = models.DateField(verbose_name='D.O.B',blank=True, null=True)

    gender_choices = [(0,'-'),(1,'Male'),(2,'Female'),(3,'Other')]
    gender = models.IntegerField(default=0, choices=gender_choices)

    last_online = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return self.email

    @property
    def last_online_time(self):
        return pretty_dt_timestamp(time=self.last_online)

from .apis.helper import pretty_dt_timestamp

class Profile(models.Model):

    user = models.OneToOneField(User,null=True, on_delete=models.CASCADE)

    picture = models.ImageField(upload_to=PathAndRename('profile_pictures'),null=True,blank=True)

    display_name = models.CharField(max_length=100, default='',null=True,blank=True)

    dob_privacy = models.BooleanField(default=False)

    dark_mode = models.BooleanField(default=False)

    @property
    def url(self):
        return reverse('gamesrec:profile',kwargs={'username':self.user.username})

    @property
    def reviews_url(self):
        return reverse('gamesrec:profile_tab',kwargs={'username':self.user.username,'profile_tab':'reviews'})

    @property
    def recs_url(self):
        return reverse('gamesrec:profile_tab',kwargs={'username':self.user.username,'profile_tab':'recs'})

    @property
    def stats_url(self):
        return reverse('gamesrec:profile_tab',kwargs={'username':self.user.username,'profile_tab':'stats'})

    @property
    def gameslist_url(self):
        return reverse('gamesrec:gameslist',kwargs={'username':self.user.username})

    @property
    def history_url(self):
        return reverse('gamesrec:profile_tab',kwargs={'username':self.user.username,'profile_tab':'history'})


    # @property
    # def lists_url(self):
    #     return reverse('gamesrec:profile_tab',kwargs={'username':self.user.username,'profile_tab':'lists'})

    @property
    def last_online(self):
        return pretty_dt_timestamp(time=self.user.last_online)

    @property
    def last_login(self):
        return pretty_dt_timestamp(time=self.user.last_login)

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session

from gamesrec.apis.session_info import location, device

class UserSession(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=500, null=True, blank=True, verbose_name='IP')
    user_agent = models.CharField(max_length=200, null=True, blank=True)
    session_key = models.CharField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    active_timestamp = models.DateTimeField(auto_now_add=True)

    @property
    def location(self):
        return location(self.ip_address)

    @property
    def device(self):
        return device(self.user_agent) if self.user_agent else ''

    @property
    def browser(self):
        return device(self.user_agent, json=True)['browser']


    @property
    def is_active_now(self):
        from .apis.helper import pretty_dt_timestamp
        a = pretty_dt_timestamp(self.active_timestamp)
        return a == 'just now'

    @property
    def expire_date(self):
        try:
            return Session.objects.get(pk=self.session_key).expire_date
        except Exception as e:
            return timezone.now()

    def update_active(self):
        self.active_timestamp = timezone.now()
        self.save()
        return self.active_timestamp

    def expire(self):
        try:
            if self.expire_date > timezone.now():
                return False
            else:
                self.end_session()
                return True
        except Exception as e:
            return None

    def end_session(self):
        try:
            Session.objects.get(pk=self.session_key).delete()
            return True
        except Exception as e:
            return False

class UserInfoLog(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    ip_address = models.CharField(max_length=500, null=True, blank=True, verbose_name='IP')
    user_agent = models.CharField(max_length=200, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        abstract = True

    @property
    def location(self):
        return location(self.ip_address)

    @property
    def device(self):
        return device(self.user_agent, json=True)['device']

    @property
    def browser(self):
        return device(self.user_agent, json=True)['browser']

class UserAction(UserInfoLog):
    action_name = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f'ACTION:{self.action_name}, {self.timestamp}'

class UsageLog(UserInfoLog):
    def __str__(self):
        return f'USAGE:{self.ip_address}, {self.timestamp}'

class SearchQuery(UserInfoLog):
    query = models.TextField(null=True,blank=True)

    class Meta:
        abstract = True

class GameSearchQuery(SearchQuery):
    pass

class FriendsSearchQuery(SearchQuery):
    searched_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='searched_user')

class Game(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255,allow_unicode=True)
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    first_release_date = models.DateTimeField(null=True,blank=True)
    popularity = models.FloatField(default=0.0)
    cover = models.CharField(null=True,max_length=255)
    description =  models.TextField(null=True,blank=True)

    class Meta:
        ordering = ['-first_release_date']

    def __str__(self):
        return f'{self.id} {self.slug} {self.rating} {self.rating_count}'

    @property
    def url(self):
        kwargs={
            'igdb_id':self.id,
            'slug':slugify(self.name)
        }
        try:
            if len(kwargs['slug']) < len(self.name):
                kwargs['slug'] = self.slug
            return reverse('gamesrec:game',kwargs=kwargs)
        except Exception as e:
            kwargs['slug'] = self.slug
            return reverse('gamesrec:game',kwargs=kwargs)

    def get_game_tab_url(self, tab_name):
        kwargs = {
            'igdb_id':self.id,
            'slug':slugify(self.name),
            'tab_name':tab_name,
        }
        try:
            if len(kwargs['slug']) < len(self.name):
                kwargs['slug'] = self.slug
            return reverse('gamesrec:game_tab',kwargs=kwargs)
        except Exception as e:
            kwargs['slug'] = self.slug
            return reverse('gamesrec:game_tab',kwargs=kwargs)

    @property
    def reviews_url(self):
        return self.get_game_tab_url('reviews')

    @property
    def write_review_url(self):
        return self.get_game_tab_url('write_review')

    @property
    def recs_url(self):
        return self.get_game_tab_url('recs')

    @property
    def add_rec_url(self):
        return self.get_game_tab_url('add_rec')

    @property
    def photos_url(self):
        return self.get_game_tab_url('photos')

    @property
    def videos_url(self):
        return self.get_game_tab_url('videos')

    @property
    def stats_url(self):
        return self.get_game_tab_url('statistics')


    @property
    def title(self):
        return f'{self.name} ({self.first_release_date.date().year})'

    @property
    def year(self):
        return self.first_release_date.date().year

    @property
    def avg_rating(self):
        usrs_w_r = list(GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)) & Q(game=self)))
        usrs_w_r = [li.rating_val if li.rating_val != '-' else 0.0 for li in usrs_w_r]
        ln = len(usrs_w_r) + self.rating_count
        f_r = usrs_w_r + [self.rating for i in range(self.rating_count)]
        avg_r = round(np.average(f_r), 1) if len(f_r) > 0 else '0.0'
        return avg_r

    @property
    def avg_rating_count(self):
        usrs_w_r = list(GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)) & Q(game=self)))
        usrs_w_r = [li.rating_val if li.rating_val != '-' else 0.0 for li in usrs_w_r]
        ln = len(usrs_w_r) + self.rating_count
        return ln

    @property
    def players(self):
        return GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)) & Q(game=self)).count()

    @property
    def status_stats(self):
        from .apis.helper import pretty_largenumber_commas
        status_n = [0,1,2,3,4]
        p_count = self.players
        def stat_val(i):
            c = GameListItem.objects.filter(Q(status=i) & Q(game=self)).count()
            p = round((c/(p_count if p_count > 0 else 1))*100,1)
            v = {'name':get_title(status_names_set[i]),'y':p, 'c':pretty_largenumber_commas(c),}
            if i == 1:
                v['sliced'] = True
                v['selected'] = True
            return v
        status_c = [stat_val(i) for i in status_n]
        return status_c

    @property
    def age_stats(self):
        from .apis.helper import getAge
        age_bounds = [(13,17),(18,24),(25,34),(35,44),(45,54),(55,64),(65)]
        a = {f'{i[0]}-{i[1]}' if type(i) == tuple else f'{i}':{'p':0, 'r':0.0} for i in age_bounds}
        p_count = self.players
        for gl in GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)) & Q(game=self)):
            if not gl.user.dob:
                continue
            u_age = getAge(gl.user.dob)
            u_rating = gl.rating_val if gl.rating_val != '-' else 0.0
            for a_b in age_bounds:
                if type(a_b) == tuple:
                    if u_age >= a_b[0] and u_age <= a_b[1]:
                        a[f'{a_b[0]}-{a_b[1]}']['p'] += 1
                        a[f'{a_b[0]}-{a_b[1]}']['r'] += u_rating
                        break
                else:
                    if u_age >= a_b:
                        a[f'{a_b}']['p'] += 1
                        a[f'{a_b}']['r'] += u_rating
                        break
        b = []
        for i in a.keys():
            a[i]['r'] = a[i]['r']/(a[i]['p'] if a[i]['p'] > 0 else 1)
            a[i]['p'] = round((a[i]['p']/(p_count if p_count > 0 else 1)) * 100,1)
            a[i]['y'] = a[i]['p']
            a[i].pop('p')
            a[i]['name'] = i if '-' in i else f'{i}+'
            b.append(a[i])
        return b

    @property
    def score_stats(self):
        p_count = self.players
        a = {f'{i}': 0 for i in list_rating_choices[1:]}
        for gl in GameListItem.objects.filter((Q(status=0) | Q(status=1) | Q(status=2) | Q(status=3) | Q(status=4)) & Q(game=self)):
            if gl.rating_val != '-':
                a[f'{gl.rating_val}'] += 1
        b = []
        for i in a.keys():
            a[i] = round((a[i]/(p_count if p_count > 0 else 1))*100, 1)
            b.append({'name':i, 'y':a[i]})
        return b

    @property
    def activity_stats(self):
        from django.db.models import Count
        gl = GameListItemHistory.objects.filter(game_list_item__game__pk=self.pk).order_by('-timestamp').values('timestamp')
        a = {}
        for i in gl:
            d = i['timestamp'].date()
            if not str(d) in a:
                a[str(d)] = 1
            else:
                a[str(d)] += 1
        a = [{'name':str(i), 'y':a[i]} for i in a.keys()][:7]
        return a

    @property
    def rnd_artwork(self):
        import random
        i = self.artwork_set.all()
        cnt = i.count()
        if cnt > 0:
            return i[random.randint(0,cnt-1)].image_id
        else:
            return None

    @property
    def rnd_screenshot(self):
        import random
        i = self.screenshot_set.all()
        cnt = i.count()
        if cnt > 0:
            return i[random.randint(0,cnt-1)].image_id
        else:
            return None

class Website(models.Model):
    games = models.ManyToManyField(Game, related_name='websites')
    id = models.IntegerField(primary_key=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.id} {self.url}'


class Artwork(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    image_id = models.CharField(max_length=255,primary_key=True)

    def __str__(self):
        return f'{self.image_id} {self.game.id}'

class Screenshot(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    image_id = models.CharField(max_length=255,primary_key=True)

    def __str__(self):
        return f'{self.image_id} {self.game.id}'

class Genre(models.Model):
    games = models.ManyToManyField(Game, related_name='genres')
    id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(null=True,blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True,blank=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'

    @property
    def qpath(self):
        return f'ge={self.id}'

class Theme(models.Model):
    games = models.ManyToManyField(Game, related_name='themes')
    id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(null=True,blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True,blank=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'

    @property
    def qpath(self):
        return f'th={self.id}'

class Perspective(models.Model):
    games = models.ManyToManyField(Game, related_name='player_perspectives')
    id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(null=True,blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True,blank=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'

    @property
    def qpath(self):
        return f'pp={self.id}'

class GameMode(models.Model):
    games = models.ManyToManyField(Game, related_name='game_modes')
    id = models.IntegerField(primary_key=True)
    created_at = models.DateTimeField(null=True,blank=True)
    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True,blank=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'

    @property
    def qpath(self):
        return f'gm={self.id}'

class Platform(models.Model):
    games = models.ManyToManyField(Game, related_name='platforms')
    id = models.IntegerField(primary_key=True)
    abbreviation = models.CharField(max_length=255)
    alternative_name =  models.CharField(max_length=255)
    category =  models.IntegerField(null=True)
    created_at = models.DateTimeField(null=True,blank=True)
    name = models.CharField(max_length=255)
    platform_logo = None
    slug = models.CharField(max_length=255)
    updated_at = models.DateTimeField(null=True,blank=True)
    url = models.CharField(max_length=255)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'

    @property
    def qpath(self):
        return f'pl={self.id}'

class AgeRating(models.Model):
    games = models.ManyToManyField(Game, related_name='age_ratings')
    rating =  models.IntegerField(primary_key=True)
    category =  models.IntegerField(null=True)

    class Meta:
        ordering = ['rating']

    def __str__(self):
        return f'{self.rating} {self.category}'

    @property
    def qpath(self):
        return f"{'ar_e' if self.category == 1 else 'ar_p'}={self.rating}"


from .apis.helper import get_title

status_names_set = ['playing','completed','plan_to_play','on_hold','dropped','not_interested']

import numpy as np

list_rating_choices = ['-'] + list(np.arange(1.0, 10.5,0.5))

class GameListItem(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)

    status_names = [get_title(i) for i in status_names_set]

    status_choices = [(i,get_title(status_names_set[i])) for i in range(len(status_names_set))]
    status = models.IntegerField(default=0, choices=status_choices)

    rating_choices = [(i,str(list_rating_choices[i]) if i+1 != len(list_rating_choices) else str(int(list_rating_choices[i]))) for i in range(len(list_rating_choices))]
    rating = models.IntegerField(default=0, choices=rating_choices)

    notes = models.TextField(null=True,blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} {self.user} {self.status} {self.rating}'

    @property
    def game_slug(self):
        if self.game:
            return self.game.slug
        else:
            return None

    @property
    def rating_val(self):
        return list_rating_choices[self.rating]

    @property
    def status_val(self):
        return self.status_names[self.status]

class GameListItemHistory(models.Model):
    status_names = [get_title(i) for i in status_names_set]

    game_list_item = models.ForeignKey(GameListItem, null=True, on_delete=models.CASCADE)

    status_choices = [(i,get_title(status_names_set[i])) for i in range(len(status_names_set))]
    status = models.IntegerField(default=0, choices=status_choices)

    rating_choices = [(i,str(list_rating_choices[i]) if i+1 != len(list_rating_choices) else str(int(list_rating_choices[i]))) for i in range(len(list_rating_choices))]
    rating = models.IntegerField(default=0, choices=rating_choices)

    notes = models.TextField(null=True,blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} {self.timestamp} {self.status} {self.rating}'

    @property
    def game_slug(self):
        if self.game_list_item.game:
            return self.game_list_item.game.slug
        else:
            return None

    @property
    def user_username(self):
        if self.game_list_item.user:
            return self.game_list_item.user.username
        else:
            return None

    @property
    def rating_val(self):
        return list_rating_choices[self.rating]

    @property
    def status_val(self):
        return self.status_names[self.status]

    @property
    def timestamp_pretty(self):
        return pretty_dt_timestamp(time=self.timestamp)

class GameReview(models.Model):
    #user foreign key
    #game one to one
    pass

class AlternativeName(models.Model):
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)
    id = models.IntegerField(primary_key=True)
    comment = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.id} {self.name}'


class API(models.Model):
    key = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'{self.key} {self.timestamp}'

class UserRatings(models.Model):
    data = JSONField()

    def __str__(self):
        import json
        return f'{len(json.loads(self.data))} user rating(s)'

    class Meta:
        verbose_name_plural = "User Ratings"

    @property
    def count(self):
        import json
        return 0 if type(self.data) == dict else len(json.loads(self.data))

class GuestRecommendations(models.Model):
    data = JSONField()

    def __str__(self):
        import json
        return f'{len(json.loads(self.data))} recommendation(s)'

    class Meta:
        verbose_name_plural = "Guest Recommendations"

    @property
    def count(self):
        import json
        return 0 if type(self.data) == dict else len(json.loads(self.data))


class Review(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)

    helpful_users = models.ManyToManyField(User, related_name='helpful')

    not_helpful_users = models.ManyToManyField(User, related_name='unhelpful')

    r_vals = list_rating_choices

    rating_choices = [(i,str(list_rating_choices[i]) if i+1 != len(list_rating_choices) else str(int(list_rating_choices[i]))) for i in range(len(list_rating_choices))]

    r = [
        {'id':'star_story','name':'Story','h_name':'story'},
        {'id':'star_char_vis','name':'Characters/Visuals','h_name':'char_vis'},
        {'id':'star_music', 'name':'Music','h_name':'music'},
        {'id':'star_replay', 'name': 'Replay value','h_name':'replay'},
        {'id':'star_overall', 'name':'Overall','h_name':'overall'}
    ]

    story = models.IntegerField(default=0, choices=rating_choices)
    char_vis = models.IntegerField(default=0, choices=rating_choices)
    music = models.IntegerField(default=0, choices=rating_choices)
    replay = models.IntegerField(default=0, choices=rating_choices)
    overall = models.IntegerField(default=0, choices=rating_choices)

    spoiler = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    dropped = models.BooleanField(default=False)

    review_text = models.TextField(null=True,blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} {self.user}'

    @property
    def game_slug(self):
        if self.game:
            return self.game.slug
        else:
            return None

    @property
    def ratings(self):
        rs = {
            'story':list_rating_choices[self.story],
            'char_vis':list_rating_choices[self.char_vis],
            'music':list_rating_choices[self.music],
            'replay':list_rating_choices[self.replay],
            'overall':list_rating_choices[self.overall]
        }
        return rs

    @property
    def ratings_list(self):
        rs = [
            list_rating_choices[self.story],
            list_rating_choices[self.char_vis],
            list_rating_choices[self.music],
            list_rating_choices[self.replay],
            list_rating_choices[self.overall]
        ]
        rs = [i if i != '-' else 0.0 for i in rs]
        return rs


    @property
    def edit_review_url(self):
        return reverse('gamesrec:profile_tab_sub',kwargs={'username':self.user.username,'profile_tab':'edit_review', 'id':self.pk})

class Rec(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)

    similar_game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE, related_name='similar_game')

    likes = models.ManyToManyField(User, related_name='rec_likes')

    rec_text = models.TextField(null=True,blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.pk} {self.user}'

    @property
    def game_slug(self):
        if self.game:
            return self.game.slug
        else:
            return None

    @property
    def edit_rec_url(self):
        return reverse('gamesrec:profile_tab_sub',kwargs={'username':self.user.username,'profile_tab':'edit_rec', 'id':self.pk})


from mptt.models import MPTTModel, TreeForeignKey

class Comment(MPTTModel):

    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)

    text = models.TextField(null=True,blank=True)

    likes = models.ManyToManyField(User, related_name='c_likes')

    dislikes = models.ManyToManyField(User, related_name='c_dislikes')

    public = models.BooleanField(default=True)

    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    mention = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='mention_user')

    timestamp = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ['timestamp']


class GameComment(Comment):

    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE)

from .signals import *
