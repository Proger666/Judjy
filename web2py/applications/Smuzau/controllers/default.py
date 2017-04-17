# -*- coding: utf-8 -*-
### required - do no delete

from transliterate import translit


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()

def search_or(tags=[]):

    #Search through each tags inside many-to-many relation
    # with OR
 t_smoothie = db.t_smoothie
 ingr = db.t_ingredient
 ingr_smuz = db.ingr_smuz
 subquery = db(db.t_ingredient.id.belongs(tags)).select(db.t_ingredient.id)
 rows = db(t_smoothie.id==ingr_smuz.smuz)\
 (ingr_smuz.ingr.belongs(subquery)).select(
     t_smoothie.ALL,
     orderby=t_smoothie.id,
     groupby=t_smoothie.id,
     distinct=True)
 return rows


def search_and(tags=[]):
    # Search through each tags inside many-to-many relation
    # with AND
    t_smoothie = db.t_smoothie
    ingr = db.t_ingredient
    ingr_smuz = db.ingr_smuz
    n = len(tags)
    subquery = db(ingr.id.belongs(tags)).select(ingr.id)
    rows = db(t_smoothie.id == ingr_smuz.smuz) \
        (ingr_smuz.ingr.belongs(subquery)).select(
        t_smoothie.ALL,
        orderby=t_smoothie.id,
        groupby=t_smoothie.id,
        having=t_smoothie.id.count() == n)
    if len(rows) == 0:
        rows = search_or(tags)
    return rows

def filter_smuz():
    # if nothing chosen select all
    if request.vars.ingr is None:
        smuzs = db(db.t_smoothie).select()
    else:
        #   Create list from variables splited by separator
        ids = request.vars.ingr.split("%s")
        smuzs = search_and(ids)
        # find anything with tags (from var list)

    # create recipe snippets as pure HTML (XML)
    result = []
    if len(smuzs) == 0:
        return DIV(P('Пустота вокруг...'), _class="text_size_24 page-header center").xml()

    for smuz in smuzs:
        # TODO: Multiple recipe per smoothie
        recipe = db(db.t_recipe.f_smoothie == smuz.id).select().first()
        i = 0
        rating_XML = ""
        while i < settings.max_rating:
            if i < smuz.f_rating:
                rating_XML += XML('<li class="c-rating__item is-active" data-index="' + str(i) + '" ></li>')
            else:
                rating_XML += XML('<li class="c-rating__item" data-index="' + str(i) + '" ></li>')
            i += 1
        result.append((DIV(
            DIV(
                IMG(_src=URL('default', 'download', args=smuz.f_image), _class="img-responsive"), _class="thumbnail"),
            DIV(
                A(
                    H4(smuz.f_name, _style="text-align:center"),
                    _href=URL('default', 'smuzau', vars=dict(smooth_name=smuz.f_name_lat))),
                P(recipe.f_fulltext),
                DIV(P("Оценили", _class="pull-right grid-col-reviewed"),
                    XML('<main class="o-content"> '
                        '<div class="o-container"> '
                        '<div class="o-section"> '
                        '<ul class="c-rating"> '
                        + rating_XML +
                        '<li class="grid_col_review_count"> ' + str(smuz.f_rated_count) + '</li>'
                                                                                          ' </div>'
                                                                                          ' </div>'
                                                                                          ' </main>'
                        ), _class="ratings"),
                _class="caption"), _class="col-sm-4 col-lg-4 col-md-4").xml()))

    return result





### end requires
def index():
    ingredients = db(db.t_ingredient).select()
    smuzs = db(db.t_smoothie).select()
    filter_smuz()
    #            orderby=~count)[0].t_product.id
    return locals()


def error():
    return dict()


def smuzau():
    if not request.vars.smooth_name:
        return ''
    smothie = db(db.t_smoothie.f_name_lat == request.vars.smooth_name).select().first()
    #ingrs = smothie.ingredients
    # TODO: Lazy magic - learn
    ingrs = smothie.ingr_smuz.select(db.ingr_smuz.ingr)
    recipe = db(db.t_recipe.f_smoothie == smothie.id).select().first()
    rating = smothie.f_rating
    return locals()


def create_default_rating_row(id):
    db.t_rating.insert(f_smoothie=id)
    db.commit()
    pass


def smuz_voting():
    # get rating Record for asked soothie
    rating_to_update = db(db.t_rating.f_smoothie == request.vars.id).select().first()
    if rating_to_update is None:
        create_default_rating_row(request.vars.id)
        rating_to_update = db(db.t_rating.f_smoothie == request.vars.id).select().first()
    # construct needed field from db
    star_count = 'f_rated_' + request.vars.rating + '_count'
    R = rating_to_update[star_count] + 1
    # increase counter by 1
    rating_to_update[star_count] = R
    # flush to db
    rating_to_update.update_record()

    # FIXME: god dat is ugly. FIX ME FOR GOD SAKE!!
    # Calculate MEAN rating
    votes_count = (rating_to_update.f_rated_5_count + rating_to_update.f_rated_4_count +
                   rating_to_update.f_rated_3_count + rating_to_update.f_rated_2_count + rating_to_update.f_rated_1_count)

    new_rating = (rating_to_update.f_rated_5_count * 5 +
                  rating_to_update.f_rated_4_count * 4 +
                  rating_to_update.f_rated_3_count * 3 +
                  rating_to_update.f_rated_2_count * 2 +
                  rating_to_update.f_rated_1_count * 1) / votes_count

    # flush to db new MEAN rating
    rating_to_update.update_record(f_rating=new_rating)
    db(db.t_smoothie.id == request.vars.id).update(f_rating=new_rating, f_rated_count=votes_count)
    # smuz_to_update.update_record(f_rated_count = cur_rateNum + 1)

    return locals()


def search_string():
    return FORM(DIV(INPUT(_name='search_', _title='Все смузяу тут',
                          _class='form-control input-normal', _style='center-block form-control input-lg',
                          _id='product_s_str', _placeholder='Найдите ваш смузяу...'),
                    SPAN(
                        BUTTON(I(_class='glyphicon glyphicon-search'), _type='submit', _class='btn btn-sm btn-primary'),
                        _class='input-group-btn'), _class="input-group"),
                _class="navbar-form", _role="search").xml()

def add_smuz():
   form = SQLFORM(db.t_smoothie)
   if form.process().accepted:
       response.flash = 'form accepted'
   elif form.errors:
       response.flash = 'form has errors'
   return dict(form=form)

def download():
    return response.download(request, db)

