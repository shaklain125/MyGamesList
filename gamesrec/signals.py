from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver, Signal
from .models import *
from gamesrec.apis.helper import *
from django.utils import timezone

from gamesrec.apis.session_info import *
from django.contrib.sessions.models import Session

u_logged_in = Signal(providing_args=['instance', 'request'])

def u_logged_in_receiver(sender, instance, request, *args, **kwargs):
    UserSession.objects.create(user=instance,ip_address=get_ip(request), user_agent=get_user_agent(request), session_key=request.session.session_key)

u_logged_in.connect(u_logged_in_receiver)

@receiver(pre_delete, sender=Session)
def pre_delete_session(sender, instance, **kwargs):
    try:
        UserSession.objects.get(session_key=instance.pk).delete()
    except Exception as e:
        pass

@receiver(post_delete, sender=UserSession)
def post_delete_session(sender, instance, **kwargs):
    try:
        instance.end_session()
    except Exception as e:
        pass

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance,display_name=instance.username)
        instance.profile.save()

# post_save.connect(create_profile, sender=User)

@receiver(post_save, sender=GameListItem)
def add_rating_history(sender, instance, created, **kwargs):
    if created:
        gh = GameListItemHistory.objects.create(game_list_item=instance, status=instance.status, rating=instance.rating, notes=instance.notes)
        gh.save()
    else:
        if 'update_fields' in kwargs and kwargs['update_fields'] != None and 'updated_at' in kwargs['update_fields']:
            return
        last = GameListItemHistory.objects.filter(game_list_item=instance).order_by('-timestamp')[0]
        match = GameListItemHistory.objects.filter(game_list_item=instance, status=instance.status, rating=instance.rating, notes=instance.notes).order_by('-timestamp')
        match = match[0] if match.exists() else None

        if last != match:
            gh = GameListItemHistory.objects.create(game_list_item=instance, status=instance.status, rating=instance.rating, notes=instance.notes)
            gh.save()

@receiver(post_save, sender=GameListItemHistory)
def on_rating_history_save(sender, instance, created, **kwargs):
    if created:
        instance.game_list_item.updated_at = timezone.now()
        instance.game_list_item.save(update_fields=['updated_at'])

# post_save.connect(add_rating_history, sender=GameListItem)


@receiver(post_save, sender=Game)
def create_game(sender, instance, created, **kwargs):
    # if created:
    #     pass
    #     # print('Game Created', instance.id)
    # else:
    if hasattr(instance, '_extra'):
        def relate(obj, obj_type):
            nonlocal instance
            if obj == None:
                return
            obj['created_at'] = str(epoch_to_dateUTC(obj['created_at'] if 'created_at' in obj else None))
            obj['updated_at'] = str(epoch_to_dateUTC(obj['updated_at'] if 'updated_at' in obj else None))
            if obj_type == Platform:
                ex = ['platform_logo','versions','websites','generation','product_family','summary']
                [obj.pop(e,None) for e in ex]
            obj_m = obj_type(**obj)
            m = obj_type.objects.filter(**obj)
            m = m[0] if m.exists() else None
            if m == None:
                obj_m.save()
                if not obj_type.objects.filter(games=instance, id=obj_m.pk).exists():
                    obj_m.games.add(instance)
            else:
                if not obj_type.objects.filter(games=instance, id=m.pk).exists():
                    m.games.add(instance)

        def exec_rel(o_t, func):
            nonlocal instance
            for t in instance._extra.keys():
                if instance._extra[t] == None or not t in o_t.keys():
                    continue
                [func(o,o_t[t]) for o in instance._extra[t]]

        o_t = {'genres':Genre, 'themes':Theme, 'perspectives':Perspective,'game_modes':GameMode, 'platforms': Platform}
        exec_rel(o_t,relate)

        def relate2(obj, obj_type):
            nonlocal instance
            if obj == None:
                return
            obj['game'] = instance
            obj_m = obj_type(**obj)
            m = obj_type.objects.filter(**obj)
            m = m[0] if m.exists() else None
            # print('RELATE2',m,obj_m)
            if m == None:
                obj_m.save()

        o_t2 = {'alternative_names':AlternativeName}
        exec_rel(o_t2,relate2)

        def relate4(obj, obj_type):
            nonlocal instance
            if (obj == None) or (type(obj) == dict and not 'image_id' in obj) or (type(obj) != dict):
                return
            obj = {'image_id':obj['image_id'], 'game': instance}
            obj_m = obj_type(**obj)
            m = obj_type.objects.filter(**obj)
            m = m[0] if m.exists() else None
            # print('RELATE2',m,obj_m)
            if m == None:
                obj_m.save()

        o_t4 = {'artworks':Artwork, 'screenshots':Screenshot}
        exec_rel(o_t4,relate4)

        o_t3 = {'age_ratings':AgeRating}

        def relate3(obj, obj_type):
            nonlocal instance
            if obj == None:
                return
            [obj.pop(ex, None) for ex in ['content_descriptions', 'synopsis','id']]
            obj_m = obj_type(**obj)
            m = obj_type.objects.filter(**obj)
            m = m[0] if m.exists() else None
            if m == None:
                obj_m.save()
                if not obj_type.objects.filter(games=instance, rating=obj_m.pk).exists():
                    obj_m.games.add(instance)
            else:
                if not obj_type.objects.filter(games=instance, rating=m.pk).exists():
                    m.games.add(instance)
        exec_rel(o_t3,relate3)
            # print(instance._extra,)
        # print('Game', instance.id)





        def relate5(obj, obj_type):
            nonlocal instance
            if obj == None:
                return
            [obj.pop(ex,None) for ex in ['category', 'trusted','game']]
            obj_m = obj_type(**obj)
            m = obj_type.objects.filter(**obj)
            m = m[0] if m.exists() else None
            if m == None:
                obj_m.save()
                if not obj_type.objects.filter(games=instance, id=obj_m.pk).exists():
                    obj_m.games.add(instance)
            else:
                if not obj_type.objects.filter(games=instance, id=m.pk).exists():
                    m.games.add(instance)

        o_t = {'websites':Website}
        exec_rel(o_t,relate5)
