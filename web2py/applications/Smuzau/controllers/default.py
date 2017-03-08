# -*- coding: utf-8 -*-
### required - do no delete

from transliterate import translit


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


### end requires
def index():
    print(translit(u"Фрукты и Йогурт смузи", 'ru', reversed=True))
    return dict()


def error():
    return dict()


def smuzau():
    if not request.vars.smooth_name:
        return ''
    smothie = db(db.t_smoothie.f_name_lat == request.vars.smooth_name).select().first()
    rating = smothie.f_rating
    return locals()
