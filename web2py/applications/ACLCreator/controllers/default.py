# -*- coding: utf-8 -*-
### required - do no delete
import datetime

import StringIO
from pip._vendor.requests.packages.urllib3.util import url
import pandas as pd
import csv
import io
from os import path

def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


def createRule(zone_name, src_ip, destIP, destPort, type, same_IP_h, obj_pref):
    result = StringIO.StringIO()
    if type == 'subnet-host':
        result.write('abc')
    elif type == 'host-host':
        result.write('cvsa')
    return result


def zones():
    rows = db(db.t_cache.f_name.like('%Segment%')).select()
    if request.vars.segment_file is not None and len(request.vars) is not 0:
        # bunch of defauls
        sameIPhost = request.vars.maxH
        objPref = request.vars.objpref
        separator = '-'
        ports = db(db.t_cache.f_name.like(request.vars.filename)).select(db.t_cache.f_ports).first().f_ports
        if hasattr(request.vars.segment_file, 'file'):
            f_id = str(datetime.datetime.now().microsecond) + request.vars.segment_file.filename
            db.t_cache.insert(f_data=request.vars.segment_file, f_name=f_id, f_ports=request.vars.ports)
            db.commit()
        else:
            f_id = request.vars.segment_file
        xl = pd.ExcelFile(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(f_id)).select().first().f_data)[1])
        # remove unicode and cast to STR
        sheet_names = [str(x) for x in xl.sheet_names]
        sheets = xl.book.sheets()
        data = pd.read_csv(
            db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
        for sheet in sheets:
            zone_rules = StringIO.StringIO
            zone_ips = [str(x) for x in sheet.col_values(1)]
            # remove unicode and cast to STR
            zone_name = str(sheet.name)
            # filter by label source.ip and find all ip that is belongs to zone inside source DATA
            source_tree = data[(data['source.ip: Descending'].isin(zone_ips) & (data['dest.port: Descending'] <= int(ports)))]
            # Group by DEST IP - tree to DEST ip address so dest ip - list of all who interacte with it
            dest_tree = source_tree.groupby(['dest.ip: Descending', 'dest.port: Descending', 'source.ip: Descending'],
                                as_index=False).mean()
            # group by dest ip and count non unique values (source ip) to count how much src ip connects to same dst and port
            non_uniq_src_count = dest_tree.groupby(['dest.ip: Descending', 'dest.port: Descending'])['source.ip: Descending'].nunique()
            for dest_port, hitcount in non_uniq_src_count.iteritems():
                if hitcount >= sameIPhost:
                    zone_rules.write(zone_name + separator +
                                     zone_name + '_IP' + separator +
                                     + dest_port[0] + separator + dest_port[1] + separator
                                     + 'comment: number of hist for this dest ip and port = ' + hitcount + ',')
                else:
                    temp_data = dest_tree.loc[dest_tree['dest.ip: Descending'] == '10.127.253.19', ['source.ip: Descending',
                                                                                        'dest.ip: Descending',
                                                                                        'dest.port: Descending']]
                    for index, row in temp_data.iterrows():
                        zone_rules.write(zone_name + separator +
                                            row['source.ip: Descending'] + separator +
                                         row['dest.ip: Descending']




    return locals()

def table():
    data = pd.read_csv(db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
    ports = db(db.t_cache.f_name.like(request.vars.filename)).select(db.t_cache.f_ports).first()
    src_ip = data['source.ip: Descending'].unique()
    return locals()


### end requires
def index():
    current_files = db(db.t_cache.f_name.like('%data%')).select()
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
