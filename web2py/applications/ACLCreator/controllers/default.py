# -*- coding: utf-8 -*-
### required - do no delete
def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


### end requires
def index():
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        db.t_cache.insert(f_data=request.vars.csv_file, f_name=request.vars.csv_file.filename)
        db.commit()
        redirect(URL('default', 'graph', vars={'file_name':request.vars.csv_file.filename}))
    return locals()

def graph():
    csv_file = db(db.t_cache.f_name.like(request.vars.file_name)).select().first()
    return locals()

def error():
    return dict()


@auth.requires_login()
def data_manage():
    form = SQLFORM.smartgrid(db.t_data, onupdate=auth.archive)
    return locals()


@auth.requires_login()
def cache_manage():
    form = SQLFORM.smartgrid(db.t_cache, onupdate=auth.archive)
    return locals()
