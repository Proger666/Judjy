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

def zones():
    if request.vars.segment_file is not None and len(request.vars) is not 0:
        ports = db(db.t_cache.f_name.like(request.vars.filename).select(db.t_cache.f_ports).first())
        f_id = str(datetime.datetime.now().microsecond) + request.vars.segment_file.filename
        db.t_cache.insert(f_data=request.vars.segment_file, f_name=f_id, f_ports=request.vars.ports)
        db.commit()
        xl = pd.ExcelFile(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(f_id)).select().first().f_data)[1])
        # remove unicode and cast to STR
        sheet_names = [str(x) for x in xl.sheet_names]
        sheets = xl.book.sheets()
        data = pd.read_csv(
            db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])

        for sheet in sheets:
            zone_ips = [str(x) for x in sheet.col_values(1)]
            # remove unicode and cast to STR
            zone_name = str(sheet.name)
            # filter by label source.ip and find all ip inside it
            source_tree = data[(data['source.ip: Descending'].isin(zone_ips) & (data['dest.port: Descending'] <= int(ports)))]
            num_rows = sheet.nrows - 1
            num_cells = sheet.ncols - 1
            curr_row = -1
            while curr_row < num_rows:
                curr_row += 1
                row = sheet.row(curr_row)
                curr_cell = -1
                while curr_cell < num_cells:
                    curr_cell += 1
                    # Cell Types: 0=Empty, 1=Text, 2=Number, 3=Date, 4=Boolean, 5=Error, 6=Blank
                    cell_type = sheet.cell_type(curr_row, curr_cell)
                    cell_value = sheet.cell_value(curr_row, curr_cell)
                    # get cell data and column name

    return locals()

def table():
    data = pd.read_csv(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
    ports = db(db.t_cache.f_name.like(request.vars.filename)).select(db.t_cache.f_ports).first()
    src_ip = data['source.ip: Descending'].unique()
    return locals()


### end requires
def index():
    current_files = db(db.t_cache.f_data).select()
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        f_id = str(datetime.datetime.now().microsecond) + request.vars.csv_file.filename
        db.t_cache.insert(f_data=request.vars.csv_file, f_name=f_id, f_ports=request.vars.ports)
        db.commit()
        redirect(URL('default', 'table', vars={'filename':f_id, 'ports':request.vars.ports}))
    return locals()


def graph():
    csv_file = db(db.t_cache.f_name.like(request.vars.filename)).select().first()
    data = pd.read_csv(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
    data = data.loc[(data['source.ip: Descending'] == request.vars.ip)
                    & (data['dest.port: Descending'] <= int(request.vars.ports)),
                    ['dest.ip: Descending', 'dest.port: Descending']]
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
