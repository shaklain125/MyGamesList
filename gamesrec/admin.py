from django.contrib import admin
from .models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group

from .forms import UserAdminCreationForm, UserAdminChangeForm

admin.site.site_header = 'MyGamesList Dashboard'

class GeneralUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('email', 'password','last_login','joined',)}),
        # ('Personal info', {'fields': ()}),
        ('Permissions', {'fields': ('is_admin',)}),
    )
    readonly_fields = ['last_login','joined']
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

@admin.register(User)
class UserAdmin(GeneralUserAdmin):
    # The forms to add and change user instances
    # form = UserAdminChangeForm
    # add_form = UserAdminCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ['email','pk']
    list_filter = ()
    fieldsets = (
        (None, {'fields': ['email', 'password']}),
        ('Personal info', {'fields': ['gender', 'dob']}),
        ('Account', {'fields': ['joined','last_login','last_online_time']}),
        # ('Permissions', {'fields': ('admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    # add_fieldsets = (
    #     (None, {
    #         'classes': ('wide',),
    #         'fields': ('email', 'password1', 'password2')}
    #     ),
    # )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readonly_fields += ['last_online_time']

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = 'ip_address', 'user', 'location', 'device', 'created', 'active_timestamp', 'expire_date',
    search_fields = ()
    raw_id_fields = 'user',
    exclude = 'session_key',

@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = 'ip_address', 'user','action_name' ,'location','browser', 'device', 'timestamp',
    search_fields = ()
    raw_id_fields = 'user',


@admin.register(UsageLog)
class UsageLogAdmin(admin.ModelAdmin):
    list_display = 'ip_address', 'user', 'location','browser', 'device', 'timestamp',
    search_fields = ()
    raw_id_fields = 'user',

@admin.register(GameSearchQuery)
class GameSearchQueryAdmin(admin.ModelAdmin):
    list_display = 'ip_address', 'user', 'location', 'device', 'query', 'timestamp',
    search_fields = ()
    raw_id_fields = 'user',

@admin.register(FriendsSearchQuery)
class FriendsSearchQueryAdmin(admin.ModelAdmin):
    list_display = 'ip_address', 'user', 'location', 'device', 'searched_user', 'timestamp',
    search_fields = ()
    raw_id_fields = 'user',

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user','last_online','last_login']
    list_filter = ()
    fieldsets = (
        ('User Details', {'fields': ['user','display_name','picture']}),
        ('Preferences', {'fields': ['dob_privacy','dark_mode']}),
        (None, {'fields': ['last_online','last_login']}),
    )
    filter_horizontal = ()
    readonly_fields = ['user','last_online','last_login']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # list_display = ['game_slug','pk','user','status','rating', 'timestamp', 'updated_at']
    list_filter = ()
    fieldsets = (
        ('Added By', {'fields': ['user']}),
        (None, {'fields': ['review_text','timestamp','updated_at']}),
    )
    filter_horizontal = ()
    readonly_fields = ['user', 'timestamp', 'updated_at']


@admin.register(Rec)
class RecAdmin(admin.ModelAdmin):
    # list_display = ['game_slug','pk','user','status','rating', 'timestamp', 'updated_at']
    list_filter = ()
    fieldsets = (
        ('Added By', {'fields': ['user']}),
        (None, {'fields': ['rec_text','timestamp','updated_at']}),
    )
    filter_horizontal = ()
    readonly_fields = ['user', 'timestamp', 'updated_at']

@admin.register(GameListItem)
class GameListItemAdmin(admin.ModelAdmin):
    list_display = ['game_slug','pk','user','status','rating', 'timestamp', 'updated_at']
    list_filter = ()
    fieldsets = (
        ('Added By', {'fields': ['user']}),
        ('Game', {'fields': ['game','status','rating','notes']}),
        # (None, {'fields': ['last_online']}),
    )
    filter_horizontal = ()
    readonly_fields = ['user']

@admin.register(GameListItemHistory)
class GameListItemHistoryAdmin(admin.ModelAdmin):
    list_display = ['game_slug','pk','user_username','timestamp','status','rating']
    list_filter = ()
    fieldsets = (
        (None, {'fields': ['status','rating','notes', 'timestamp']}),
        # (None, {'fields': ['last_online']}),
    )
    filter_horizontal = ()
    readonly_fields = ['timestamp']


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ['image_tag','slug','id','rating','rating_count','popularity', 'first_release_date']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Game Info.', {'fields': ['id','name', 'slug', 'rating','rating_count','popularity','cover','first_release_date','description']}),
        (None, {'fields':['image_tag']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    list_filter = ['first_release_date']
    readonly_fields = ['id','name','slug','rating','rating_count','cover','popularity','image_tag','first_release_date','description']

    def image_tag(self, obj):
        from django.utils.safestring import mark_safe
        return mark_safe(f'<img src="{obj.cover}"  width="55"/>')
    image_tag.short_description = 'Cover'


@admin.register(AlternativeName)
class AlternativeNameAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','comment', 'game']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details.', {'fields': ['id','name', 'comment']}),
    )
    search_fields = ['id','name']
    filter_horizontal = ()
    readonly_fields = ['id', 'name','comment']


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ['image_id','game']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details.', {'fields': ['image_id']}),
    )
    search_fields = ['image_id', 'game__id']
    filter_horizontal = ()
    readonly_fields = ['image_id']


@admin.register(Screenshot)
class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ['image_id','game']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details.', {'fields': ['image_id']}),
    )
    search_fields = ['image_id', 'game__id']
    filter_horizontal = ()
    readonly_fields = ['image_id']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug','created_at','updated_at']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details.', {'fields': ['id','name', 'slug','created_at','updated_at']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    readonly_fields = ['id','name','slug','created_at','updated_at']


@admin.register(Website)
class WebsiteAdmin(admin.ModelAdmin):
    list_display = ['id', 'url']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details.', {'fields': ['id','url']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','url']
    filter_horizontal = ()
    readonly_fields = ['id','url']


@admin.register(Theme)
class ThemeAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug','created_at','updated_at']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['id','name', 'slug','created_at','updated_at']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    readonly_fields = ['id','name','slug','created_at','updated_at']


@admin.register(Perspective)
class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug','created_at','updated_at']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['id','name', 'slug','created_at','updated_at']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    readonly_fields = ['id','name','slug','created_at','updated_at']



@admin.register(GameMode)
class GameModeAdmin(admin.ModelAdmin):
    list_display = ['id', 'slug','created_at','updated_at']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['id','name', 'slug','created_at','updated_at']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    readonly_fields = ['id','name','slug','created_at','updated_at']


@admin.register(Platform)
class PlatformAdmin(admin.ModelAdmin):
    list_display = ['id','name', 'slug','abbreviation','alternative_name','category','created_at','updated_at']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['id','name', 'slug','abbreviation','alternative_name','category','created_at','updated_at']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id','name','slug']
    filter_horizontal = ()
    readonly_fields = ['id','name', 'slug','abbreviation','alternative_name','category','created_at','updated_at']


@admin.register(AgeRating)
class AgeRatingAdmin(admin.ModelAdmin):
    list_display = ['rating','category']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['rating','category']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['rating','category']
    filter_horizontal = ()
    readonly_fields = ['rating','category']


@admin.register(API)
class APIAdmin(admin.ModelAdmin):
    list_display = ['id','key','timestamp']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Details', {'fields': ['id','key','timestamp']}),
        # (None, {'fields': ['last_online']})
    )
    search_fields = ['id'] #+ ['key']
    filter_horizontal = ()
    readonly_fields = ['id','key','timestamp']

@admin.register(UserRatings)
class UserRatingsAdmin(admin.ModelAdmin):
    list_display = ['id','count']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Data', {'fields': ['count']}),
    )
    filter_horizontal = ()
    readonly_fields = ['count']

@admin.register(GuestRecommendations)
class GuestRecommendationsAdmin(admin.ModelAdmin):
    list_display = ['id','count']
    list_display_links = list_display
    list_filter = ()
    fieldsets = (
        ('Data', {'fields': ['count']}),
    )
    filter_horizontal = ()
    readonly_fields = ['count']


admin.site.unregister(Group)
