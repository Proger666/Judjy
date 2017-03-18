# -*- coding: utf-8 -*-
### required - do no delete

from transliterate import translit


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


def filter_smuz():

    # if nothing chosen select all
    if request.vars.ingr is None:
        smuzs = db(db.t_smoothie).select()
    else:
        #   Create list from variables splited by separator
        ids = request.vars.ingr.split("%s")
        # find anything with tags (from var list)
        smuzs = db(db.t_smoothie.id.belongs(ids)).select()
    # create recipe snippets as pure HTML (XML)
    result = []
    for smuz in smuzs:
        # TODO: Multiple recipe per smoothie
        recipe = db(db.t_recipe.id == smuz.id).select().first()
        i = 0
        rating_XML = ""
        while i < settings.max_rating:
            if i < smuz.f_rating:
                rating_XML += XML('<li class="c-rating__item is-active" data-index="'+ str(i) + '" ></li>')
            else:
                rating_XML += XML('<li class="c-rating__item" data-index="'+ str(i) + '" ></li>')
            i += 1
        result.append ((DIV(
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
                        ),_class="ratings"),
                _class="caption"), _class="col-sm-4 col-lg-4 col-md-4").xml()))

    return result


### end requires
def index():
    ingredients = db(db.t_ingredient).select()
    smuzau = []

    # Select all records and count em by ID result list then filter by count in descending order take 0 row and
    # extract id
    # top_prod = db(db.t_smoothie.id == db.t_review.f_product).select(db.t_product.id, count, groupby=db.t_product.id,
    smuzs = db(db.t_smoothie).select()
    #            orderby=~count)[0].t_product.id
    return locals()


def error():
    return dict()


def smuzau():
    if not request.vars.smooth_name:
        return ''
    smothie = db(db.t_smoothie.f_name_lat == request.vars.smooth_name).select().first()
    rating = smothie.f_rating
    return locals()


def search_string():
    return FORM(DIV(INPUT(_name='search_', _title='Все смузяу тут',
                          _class='form-control input-normal', _style='center-block form-control input-lg',
                          _id='product_s_str', _placeholder='Найдите ваш смузяу...'),
                    SPAN(
                        BUTTON(I(_class='glyphicon glyphicon-search'), _type='submit', _class='btn btn-sm btn-primary'),
                        _class='input-group-btn'), _class="input-group"),
                _class="navbar-form", _role="search").xml()
