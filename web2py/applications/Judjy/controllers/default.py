# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


### end requires
def index():
    random_product = db().select(db.t_product.ALL, limitby=(0, 1), orderby='<random>')
    form = FORM(INPUT(_name='product_s_str', _title='Введите наименование товара или услуги',
                      _class='form-control input-normal', _style='center-block form-control input-lg',
                      _id='product_s_str', _placeholder=random_product.records[0].t_product.f_name),
                SPAN(INPUT(_type='submit', _class='btn btn-lg btn-primary'), _class='input-group-btn'))
    count = db.t_product.id.count()
    # Select all records and cout em by ID result is tuple
    count_list = db(db.t_product.id == db.t_review.f_product).select(db.t_product.id, count,
                                                                     groupby=db.t_product.f_name)
    # sort Tuple and find maximum value + id filter to id
    top_prod = sorted(count_list, key=lambda x: x, reverse=True)[0].t_product.id
    # get latest comment from top_prod based on dateadded field and get only 1 item (limit by)
    latest_comm = db(db.t_review.f_product == top_prod).select(db.t_review.f_text, orderby=~db.t_review.f_dateadded,
                                                               limitby=(0, 1)).first()
    top_img = []
    if request.vars.product_s_str is not None:
        redirect(URL('default', 'products', vars=dict(product_s_str=request.vars.product_s_str)))
    return locals()


def product_selector():
    if not request.vars.product_s_str:
        return ''
    pattern = request.vars.product_s_str.capitalize() + '%'
    selected = [row.f_name for row in db(db.t_product.f_name.like(pattern)).select()]
    return ''.join([DIV(k,
                        _onclick="jQuery('#product_s_str').val('%s')" % k,
                        _onmouseover="this.style.backgroundColor='yellow'",
                        _onmouseout="this.style.backgroundColor='white'"
                        ).xml() for k in selected])


def user_search():
    if not session.m or len(session.m) == 10: session.m = []
    if request.vars.q: session.m.append(request.vars.q)
    session.m.sort()

    return locals()


def products():
    pattern = request.vars.product_s_str.capitalize() + '%'
    rows = db(db.t_product.f_name.like(pattern)).select()
    if len(rows) == 1:
        redirect(URL('default', 'product_review', vars=dict(product_s_str=rows[0].f_name)))
    return locals()


def product_review():
    description = db(db.t_product.f_name == request.vars.product_s_str).select(db.t_product.f_description).first()
    image = db(db.t_product.f_name == request.vars.product_s_str).select(db.t_product.f_image).first()
    return locals()


def error():
    return dict()


@auth.requires_login()
def review_manage():
    form = SQLFORM.smartgrid(db.t_review, onupdate=auth.archive)
    return locals()


@auth.requires_login()
def product_manage():
    form = SQLFORM.smartgrid(db.t_product, onupdate=auth.archive)
    return locals()
