# -*- coding: utf-8 -*-
### required - do no delete
from pip._vendor.requests.packages.urllib3.util import url


def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


### end requires
def index():
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        db.t_cache.insert(f_data=request.vars.csv_file, f_name=request.vars.csv_file.filename)
        db.commit()
        import csv
        import urllib2
        file = db(db.t_cache.f_name.like(request.vars.csv_file.filename)).select().first()
        url = 'http://127.0.0.1:8000'+URL('download', args=file.f_data)
        import pandas as pd
        data = pd.read_csv(url)
        from os import path
        with open(path.relpath('applications/ACLCreator/static/output.csv'), 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(['id'] + ['value'])
            prex = -1
            for i in range(data.values.shape[0]):
                    x = data.values[i][0]
                    if x is not prex:
                        spamwriter.writerow([x])
                        spamwriter.writerow([x + ';' + data.values[i][1]])
                        spamwriter.writerow(
                            [x + ';' + data.values[i][1] + ';' + str(data.values[i][2]), str(data.values[i][3])])
                        prex = x
                    else:
                        spamwriter.writerow([x + ';' + data.values[i][1]])
                        spamwriter.writerow(
                        [x + ';' + data.values[i][1] + ';' + str(data.values[i][2]), str(data.values[i][3])])
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
