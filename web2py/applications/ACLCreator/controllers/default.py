# -*- coding: utf-8 -*-
### required - do no delete
from pip._vendor.requests.packages.urllib3.util import url
import pandas as pd
import csv


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


def table():
    file = db(db.t_cache.f_name.like(request.vars.filename)).select().first()
    url = 'http://127.0.0.1:8000' + URL('download', args=file.f_data)
    data = pd.read_csv(url)
    src_ip = data['source.ip: Descending'].unique()
    dst_ip = data['source.ip: Descending'].unique()
    result = []
    result.append('<tr>')

    return locals()


### end requires
def index():
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        db.t_cache.insert(f_data=request.vars.csv_file, f_name=request.vars.csv_file.filename)
        db.commit()
        redirect(URL('default', 'table', vars={'filename':request.vars.csv_file.filename}))
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
