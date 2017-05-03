# -*- coding: utf-8 -*-
### required - do no delete
import datetime

import StringIO

import re

from IPy import IP
from pip._vendor.requests.packages.urllib3.util import url
import pandas as pd
import csv
import io
from os import path
import xlsxwriter


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


def RFC1918(ip):
    _ip = IP(str(ip))
    _ipa = _ip.iptype()
    return True if _ipa == 'PRIVATE' else False



def zones():
    rows = db(db.t_cache.f_name.like('%Segment%')).select()
    if request.vars.segment_file is not None and len(request.vars) is not 0:
        # bunch of defauls
        sameIPhost = request.vars.maxH
        objPref = request.vars.objpref
        separator = '-'
        zone_sep_f = '['
        zone_sep_s = ']'
        src_col = 'source.ip: Descending'
        dst_col = 'dest.ip: Descending'
        dstport_col = 'dest.port: Descending'
        transport_col = 'transport: Descending'
        seg_VM_col = 'VM'
        seg_IP_col = 'Ip addres'
        src_obj_name = object
        dst_obj_pref = 'obj-'

        # extract max ports that was saved in DB with data file
        maxPorts = db(db.t_cache.f_name.like(request.vars.filename)).select(db.t_cache.f_ports).first().f_ports
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

        # Objects for ACL
        objectGroup_network_tuple = {'obj_name': [],
                                     'members': []}
        objectGroup_service_tuple = {'obj_name': [],
                                     'members': []}
        objectPort_tuple = {'obj_name': ['http', 'https'],
                            'value': ['80', '443']}
        objectNetwork_tuple = {'obj_name': [],
                               'type': [],
                               'value': [],
                               'description': []}

        zone_rules_writer = []
        # zone_rules = pd.DataFrame(zone_rules_writer.getvalue(), columns=['src.ip, dst.ip, dst.port'])
        zone_rules = StringIO.StringIO()
        xl_dataframe = pd.DataFrame(columns=[seg_VM_col, seg_IP_col, 'Zone_name'])
        for sheet in sheets:
            df_tmp = xl.parse(sheet.name)
            df_tmp = df_tmp[[seg_VM_col, seg_IP_col]]
            df_tmp['Zone_name'] = sheet.name
            xl_dataframe = xl_dataframe.append(df_tmp)


        # Check if file already processed
        _tmp_row = db.t_cache(f_name='processed_' + request.vars.filename)
        if not _tmp_row:
            # Tag everything with src zone and dst zone
            for index, row in data.iterrows():
               try:
                   src_z_name = str(
                    xl_dataframe.iloc[xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[src_col]].index[0]]['Zone_name'])
               except IndexError:
                   data.ix[index, 'src_zone_name'] = 'UNKNOWN'
               else:
                   data.ix[index, 'src_zone_name'] = src_z_name
               try:
                   dst_z_name = str(
                       xl_dataframe.iloc[xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[dst_col]].index[0]]['Zone_name'])
               except IndexError:
                   data.ix[index, 'dst_zone_name'] = 'UNKNOWN'
               else:
                   data.ix[index, 'dst_zone_name'] =  dst_z_name

                # Add processed file to cache
            db.t_cache.insert(f_name='processed_' + request.vars.filename, f_str_data = data.to_csv(index=False))
        else:
            # Create buffer to feed it to pandas
          _tmp_buffer = StringIO.StringIO()
          _tmp_buffer.write(db(db.t_cache.f_name == _tmp_row.f_name).select(db.t_cache.f_str_data).first().f_str_data)
          _tmp_buffer.seek(0)
          data = pd.read_csv(_tmp_buffer)
        # delete object from memory if record already present
        del _tmp_row, _tmp_buffer




        # Create objects for all VMS from segment_file
        for index, row in xl_dataframe.iterrows():
            if row[seg_IP_col] not in objectNetwork_tuple['value']:
                if validate_ip(row[seg_IP_col]):
                    objectNetwork_tuple['value'].append(row[seg_IP_col])
                else:
                    objectNetwork_tuple['value'].append('NOT ASSIGNED')
                objectNetwork_tuple['obj_name'].append(
                    objPref + zone_sep_f + row['Zone_name'] + zone_sep_s + '_' + re.sub(' ', '_', row[seg_VM_col]))
                objectNetwork_tuple['description'].append(
                    re.sub(' ', '_', row[seg_VM_col]) + ' from ' + row['Zone_name'])
                objectNetwork_tuple['type'].append('host')

        # Create objects for all uniq services
        # Get all uniq pors via drop_duplicates and filter by maxPorts setting
        uniq_ports = data.loc[data[dstport_col] < maxPorts, [transport_col, dstport_col]].drop_duplicates()
        for index, row in uniq_ports.iterrows():
            objectPort_tuple['obj_name'].append(row[transport_col] + '_' + str(row[dstport_col]))
            objectPort_tuple['value'].append(
                'service ' + row[transport_col] + ' destination eq ' + str(row[dstport_col]))
        for zone_name in xl.book.sheet_names():
            # create group object for zone_ip
            objectNetwork_tuple['obj_name'].append('zone_' + zone_sep_f + zone_name + zone_sep_s + '_NET')
            objectNetwork_tuple['type'].append('subnet')
            objectNetwork_tuple['description'].append('Zone ' + zone_name + ' subnet')
            objectNetwork_tuple['value'].append(zone_name + '_IP')

            # Make objects dataframe
            object_data = pd.DataFrame(objectNetwork_tuple)

            zone_ips = xl_dataframe.loc[xl_dataframe['Zone_name'] == 'Main', seg_IP_col].tolist()
            # remove unicode and cast to STR
            zone_name = str(zone_name)
            # filter by label source.ip and find all ip that is belongs to zone inside source DATA and dst not the same zone
            source_tree = data[
                (data[src_col].isin(zone_ips) & (data[dstport_col] <= int(maxPorts)) & (data['dst_zone_name'] != zone_name))]

            source_tree['src_zone_name'] = zone_name
            # Group by DEST IP - tree to DEST ip address so dest ip - list of all who interacte with it
            dest_tree = source_tree.groupby(
                [dst_col, dstport_col, src_col, transport_col, 'src_zone_name', 'dst_zone_name'],
                as_index=False).mean()
            # group by dest ip and count non unique values (source ip) to count how much src ip connects to same dst and port
            aggregate_dst_hit = dest_tree.groupby([dst_col, dstport_col, transport_col])[
                src_col].nunique()

            # Create DST obj if not present
            for dest_port, hitcount in aggregate_dst_hit.iteritems():
                if RFC1918(dest_port[0]):
                    if dest_port[0] not in objectNetwork_tuple['value']:
                        objectNetwork_tuple['value'].append(dest_port[0])
                        objectNetwork_tuple['obj_name'].append(
                            objPref + dst_obj_pref  + dest_port[0])
                        objectNetwork_tuple['description'].append("LAN host")
                        objectNetwork_tuple['type'].append('host')


            object_data = pd.DataFrame(objectNetwork_tuple)
            index = 1
            for dest_port, hitcount in aggregate_dst_hit.iteritems():
                # Create src group obj
                _tmp_src_grp_obj = objPref + zone_sep_f + zone_name + zone_sep_s + '_' + 'srv_' + str(index)
                objectGroup_network_tuple['obj_name'].append(_tmp_src_grp_obj)


                if hitcount > sameIPhost:
                    abc = 1
                else:
                    grouped = dest_tree.loc[dest_tree[dst_col] == dest_port[0], [src_col]]
                    for src_ip in grouped[src_col]:
                        # Create obj for every src if not exists
                        if src_ip not in objectNetwork_tuple['value']:
                            if validate_ip(src_ip):
                                objectNetwork_tuple['value'].append(src_ip)
                            else:
                                objectNetwork_tuple['value'].append('NOT ASSIGNED')
                            objectNetwork_tuple['obj_name'].append(
                                objPref + zone_sep_f + zone_name + zone_sep_s + '_' + src_ip)
                            objectNetwork_tuple['description'].append("")
                            objectNetwork_tuple['type'].append('host')

                        # Add src obj to group
                        objectGroup_network_tuple['members'].append( _findObjectName(object_data, src_ip))

                        #Check if destination is RFC1918
                        if RFC1918(dest_port[0]):
                            _dst_obj = _findObjectName(object_data, dest_port[0])
                            zone_rules_writer.append('access-list ' + zone_name.capitalize() + '_in extended permit '
                                                     + dest_port[
                                                         2] + ' object-group ' + _tmp_src_grp_obj + ' object-group ' +
                                                     _dst_obj)
                index += 1

    return locals()

def _findObjectName(object_data,src_ip):
    result = str(object_data.iloc[object_data.loc[object_data['value'] == src_ip].index[0]]['obj_name'])
    return result


def validate_ip(s):
    s = str(s)
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True


def table():
    data = pd.read_csv(
        db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
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
        redirect(URL('default', 'table', vars={'filename': f_id, 'ports': request.vars.ports}))
    return locals()


def graph():
    csv_file = db(db.t_cache.f_name.like(request.vars.filename)).select().first()
    data = pd.read_csv(
        db.t_cache.f_data.retrieve(db(db.t_cache.f_name.like(request.vars.filename)).select().first().f_data)[1])
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
        for i in range(0, data.values.shape[0], 1):
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
