# -*- coding: utf-8 -*-
### required - do no delete
import datetime
from pip._vendor.requests.packages.urllib3.util import url
import pandas as pd
import csv
import io
from os import path


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


def table():
    data = pd.read_csv(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
    src_ip = data['source.ip: Descending'].unique()
    return locals()


### end requires
def index():
    current_files = db(db.t_cache.f_data).select()
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        f_id = str(datetime.datetime.now().microsecond) + request.vars.csv_file.filename
        db.t_cache.insert(f_data=request.vars.csv_file, f_name=f_id)
        db.commit()
        redirect(URL('default', 'table', vars={'filename':f_id}))
    return locals()


def graph():
    csv_file = db(db.t_cache.f_name.like(request.vars.filename)).select().first()
    data = pd.read_csv(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
    data = data.loc[(data['source.ip: Descending'] == request.vars.ip) & (data['dest.port: Descending'] <= 31000), ['dest.ip: Descending', 'dest.port: Descending']]
    with open(path.relpath('applications/ACLCreator/static/output.csv'), 'wb') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',')
        spamwriter.writerow(['id'] + ['value'])
        prex = -1
        root = request.vars.ip
        # Write root
        spamwriter.writerow([root, ''])
        # write all nx2 matrix
        for i in range(0,data.values.shape[0],1):
            x = data.values[i][0]
            if x is not prex:
                spamwriter.writerow([root + ';' + str(x), ''])
            spamwriter.writerow(
                    [root + ';' + x + ';' + (str(data.values[i][1]))])
            prex = x
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
