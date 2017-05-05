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

# TODO: GOD DAT UGLY!!! erase me
set_name = ['separator','First Zone Sep.','Closing Zone Sep.','Zone subnet empty pref','Destination obj prefix','Prefix for Service obj','Source IP column', 'Destination IP column', 'Destination PORT column', 'PROTOCOL column', 'VM name column', 'IP ADDRESS column']
session.set_name = set_name
if not session.set_value:
    set_value = ['-','[',']','0','obj-','DM_INLINE_SERVICE_', 'source.ip: Descending', 'dest.ip: Descending', 'dest.port: Descending', 'transport: Descending', 'VM', 'Ip addres']
    session.set_value = set_value
src_col = session.set_value[session.set_name.index('Source IP column')]
dst_col = session.set_value[session.set_name.index('Destination IP column')]
dstport_col = session.set_value[session.set_name.index('Destination PORT column')]
transport_col = session.set_value[session.set_name.index('PROTOCOL column')]
seg_VM_col = session.set_value[session.set_name.index('VM name column')]
seg_IP_col = session.set_value[session.set_name.index('IP ADDRESS column')]
# bunch of defauls
separator = session.set_value[session.set_name.index('separator')]
zone_sep_f = session.set_value[session.set_name.index('First Zone Sep.')]
zone_sep_s = session.set_value[session.set_name.index('Closing Zone Sep.')]
zonesubnetpref = session.set_value[session.set_name.index('Zone subnet empty pref')]
dst_obj_pref = session.set_value[session.set_name.index('Destination obj prefix')]
serviceObjPref = session.set_value[session.set_name.index('Prefix for Service obj')]  # 'SERVICE_srv_'

def user(): return dict(form=auth())


def download(): return response.download(request, db)


def call(): return service()


def acl():
    config = db(db.t_cache.f_name == 'config_' + request.vars.filename + '_' + request.vars.segment_file).select().first()
    return locals()


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


def broadcast(src_ip):
    s = str(src_ip)
    a = s.split('.')
    if len(a) != 4:
        return True
    if (a[3] == '255' and a[2] == '255') or (a[3] == '0' and a[2] == '0'):
        return True
    return False


def _findServiceName(service_data, dst_ip):
    result = service_data['object'][service_data]
    return result


class GroupObject:
    def __init__(self, name):
        self.members = []
        self.name = name

    def addmember(self, members):
        self.members.append(members)

    def ismember(self, member):
        return True if member in self.members else False


def createConfig(zones_rules, object_data, objectGroup_network_list, objectGroup_service_list, port_data):
    result = []
    # create all objects
    for index, row in object_data.iterrows():
        result.append('object network ' + row['obj_name'] + '\n' +
                      row['type'] + ' ' + row['value'] + '\n' +
                      'description ' + row['description'])
    for index, row in port_data.iterrows():
        result.append('object service ' + row['obj_name'] + '\n' +
                      row['value'])
    for row in objectGroup_service_list['object']:
        _str_tmp = 'object-group service ' + row.name + '\n'
        for z in row.members:
            _str_tmp = _str_tmp + 'service-object object ' + z + '\n'
        result.append(_str_tmp)
    for row in objectGroup_network_list['object']:
        _str_tmp = 'object-group network ' + row.name + '\n'
        for z in row.members:
            _str_tmp = _str_tmp + 'network-object object ' + z + '\n'
        result.append(_str_tmp)
    result = result + zones_rules
    result = '\n!\n'.join(result)
    return result

def set_session_settings():
    session.set_value = request.vars['set_value' + '[]']
    varValue = request.vars['' + '[]']


def zones():
    rows = db(db.t_data.f_name.like('%DBSG%')).select()
    set_value = session.set_value
    set_name = session.set_name
    if request.vars.segment_file is not None and len(request.vars) is not 0:
        sameIPhost = request.vars.maxH
        objPref = request.vars.objpref
        # extract max ports that was saved in DB with data file
        maxPorts = db(db.t_data.f_name.like(request.vars.filename)).select(db.t_data.f_ports).first().f_ports
        if hasattr(request.vars.segment_file, 'file'):
            f_id = str(datetime.datetime.now().microsecond) + request.vars.segment_file.filename + 'DBSG'
            db.t_data.insert(f_data=request.vars.segment_file, f_name=f_id, f_ports=request.vars.ports)
            db.commit()
        else:
            f_id = request.vars.segment_file
        xl = pd.ExcelFile(db.t_data.f_data.retrieve(db(db.t_data.f_name.like(f_id)).select().first().f_data)[1])

        # remove unicode and cast to STR
        sheet_names = [str(x) for x in xl.sheet_names]
        sheets = xl.book.sheets()
        data = pd.read_csv(
            db.t_data.f_data.retrieve(db(db.t_data.f_name.like(request.vars.filename)).select().first().f_data)[1])

        # Objects for ACL

        objectGroup_network_list = {'obj_name': [],
                                    'object': []}
        objectGroup_service_list = {'obj_name': [],
                                    'dst': [],
                                    'object': []}
        objectPort_tuple = {'obj_name': [],
                            'value': []}
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
            # REMOVE BIG PORST from data
            data = data.loc[data[dstport_col] < maxPorts]
            # Tag everything with src zone and dst zone
            for index, row in data.iterrows():
                try:
                    src_z_name = str(
                        xl_dataframe.iloc[xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[src_col]].index[0]][
                            'Zone_name'])
                except IndexError:
                    data.ix[index, 'src_zone_name'] = 'UNKNOWN'
                else:
                    data.ix[index, 'src_zone_name'] = src_z_name
                try:
                    dst_z_name = str(
                        xl_dataframe.iloc[xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[dst_col]].index[0]][
                            'Zone_name'])
                except IndexError:
                    data.ix[index, 'dst_zone_name'] = 'UNKNOWN'
                else:
                    data.ix[index, 'dst_zone_name'] = dst_z_name

            # Add processed file to cache
            db.t_cache.insert(f_name='processed_' + request.vars.filename, f_str_data=data.to_csv(index=False))
        else:
            # Create buffer to feed it to pandas
            _tmp_buffer = StringIO.StringIO()
            _tmp_buffer.write(db(db.t_cache.f_name == _tmp_row.f_name).select(db.t_cache.f_str_data).first().f_str_data)
            _tmp_buffer.seek(0)
            # load file from cache
            data = pd.read_csv(_tmp_buffer)
            del _tmp_buffer
        # delete object from memory if record already present
        del _tmp_row,

        _tmp_row = db.t_cache(f_name='config' + request.vars.filename + '_' + f_id)
        if not _tmp_row:

            # Create objects for all VMs from segment_file
            for index, row in xl_dataframe.iterrows():
                if row[seg_IP_col] not in objectNetwork_tuple['value']:
                    if validate_ip(row[seg_IP_col]):
                        objectNetwork_tuple['value'].append(row[seg_IP_col])
                    else:
                        objectNetwork_tuple['value'].append('NOT ASSIGNED')

                    zone_name = re.sub('[ ,]', '_', row['Zone_name'])
                    objectNetwork_tuple['obj_name'].append(
                        objPref + zone_sep_f + zone_name + zone_sep_s + '_' + re.sub('[ ,]', '_', row[seg_VM_col]))
                    objectNetwork_tuple['description'].append(
                        re.sub('[ ,]', '_', row[seg_VM_col]) + ' from ' + row['Zone_name'])
                    objectNetwork_tuple['type'].append('host')

            # Create objects for all uniq ports/transport
            # Get all uniq pors via drop_duplicates and filter by maxPorts setting
            uniq_ports = data.loc[data[dstport_col] < maxPorts, [transport_col, dstport_col]].drop_duplicates()
            for index, row in uniq_ports.iterrows():
                objectPort_tuple['obj_name'].append(row[transport_col] + '_' + str(row[dstport_col]))
                objectPort_tuple['value'].append(
                    'service ' + row[transport_col] + ' destination eq ' + str(row[dstport_col]))
            index_service = 1
            for zone_name in xl.book.sheet_names():
                # create group object for zone_ip
                # clear zone name from garbage
                zone_name = re.sub('[ ,]', '_', zone_name)
                if zonesubnetpref == '':
                    zonesubnetprefs = zone_name + '_IP'
                else:
                    zonesubnetprefs = zonesubnetpref
                # remove unicode and cast to STR
                zone_name = str(zone_name)
                objectNetwork_tuple['obj_name'].append('zone_' + zone_sep_f + zone_name + zone_sep_s + '_NET')
                objectNetwork_tuple['type'].append('subnet')
                objectNetwork_tuple['description'].append('Zone ' + zone_name + ' subnet')
                objectNetwork_tuple['value'].append(zonesubnetprefs)

                ######################### SORTING DATA FOR CURRENT ZONE ################################
                zone_ips = xl_dataframe.loc[xl_dataframe['Zone_name'] == 'Main', seg_IP_col].tolist()


                # filter by label source.ip and find all ip that is belongs to zone inside source DATA and dst not the same zone
                source_tree = data[
                    (data[src_col].isin(zone_ips) & (data[dstport_col] <= int(maxPorts)) & (
                        data['dst_zone_name'] != zone_name))]

                source_tree['src_zone_name'] = zone_name
                # Group by DEST IP - tree to DEST ip address so dest ip - list of all who interacte with it
                dest_tree = source_tree.groupby(
                    [dst_col, dstport_col, src_col, transport_col, 'src_zone_name', 'dst_zone_name'],
                    as_index=False).mean()
                # group by dest ip and count non unique values (source ip) to count how much src ip connects to same dst and port
                aggregate_dst_hit = dest_tree.groupby([dst_col])[src_col].nunique()
                service_dst_grp = dest_tree.groupby([dst_col, dstport_col, transport_col])[dstport_col].unique()
                port_data = pd.DataFrame(objectPort_tuple)
                ######################### END OF SORTING ################################

                # Create dst SERVICE group
                last_dst = ''
                for dst_port, garbage in service_dst_grp.iteritems():
                    if RFC1918(dst_port[0]) and not broadcast(dst_port[0]):
                        if last_dst is '' or dst_port[0] != last_dst:
                            _tmp_port_grp_obj = serviceObjPref + str(index_service)
                            # Create SERVICE object for DST if not exist
                            if _tmp_port_grp_obj not in objectGroup_service_list['obj_name']:
                                _service_obj = GroupObject(_tmp_port_grp_obj)
                                objectGroup_service_list['obj_name'].append(_tmp_port_grp_obj)
                                objectGroup_service_list['dst'].append(dst_port[0])
                                objectGroup_service_list['object'].append(_service_obj)
                                last_dst = dst_port[0]
                                index_service += 1
                        else:
                            _tmp_port_grp_obj = serviceObjPref + str(index_service - 1)

                        # Check if current port already member of current object else ADD MEMBER
                        # TUPLE [FIRST NAME] [ GET INDEX OF ELEMNT]. CALL MEMBER FUNC
                        if not objectGroup_service_list['object'][
                            objectGroup_service_list['obj_name'].index(_tmp_port_grp_obj)].ismember(
                                            dst_port[2] + '_' + str(dst_port[1])):
                            objectGroup_service_list['object'][
                                objectGroup_service_list['obj_name'].index(_tmp_port_grp_obj)].addmember(
                                dst_port[2] + '_' + str(dst_port[1]))
                        if dst_port[0] not in objectNetwork_tuple['value']:
                            objectNetwork_tuple['value'].append(dst_port[0])
                            objectNetwork_tuple['obj_name'].append(
                                objPref + dst_obj_pref + dst_port[0])
                            objectNetwork_tuple['description'].append("LAN host")
                            objectNetwork_tuple['type'].append('host')

                # Make objects dataframe
                object_data = pd.DataFrame(objectNetwork_tuple)
                index = 1
                for dest_port, hitcount in aggregate_dst_hit.iteritems():

                    # Check if destination is RFC1918 and not broadcast or net adress
                    if RFC1918(dest_port) and not broadcast(dest_port):
                        _service_obj = objectGroup_service_list['object'][
                            objectGroup_service_list['dst'].index(dest_port)]
                        if hitcount >= int(sameIPhost):
                            _dst_obj = _findObjectName(object_data, dest_port)
                            _service_obj = objectGroup_service_list['object'][
                                objectGroup_service_list['dst'].index(dest_port)]
                            zone_rules_writer.append(
                                'access-list ' + re.sub(' ', '_',
                                                        zone_name.capitalize()) + '_in extended permit object-group '
                                + _service_obj.name + ' object-group ' + _findObjectName(object_data,
                                                                                         zonesubnetprefs) + ' object-group ' + _dst_obj)
                        else:
                            grouped = dest_tree.loc[dest_tree[dst_col] == dest_port, [src_col]]

                            # Create SERVICE object for SRC if not exist
                            _tmp_src_grp_obj = objPref + zone_sep_f + zone_name + zone_sep_s + '_' + 'srv_' + str(index)
                            if _tmp_src_grp_obj not in objectGroup_network_list['obj_name']:
                                _network_obj = GroupObject(_tmp_src_grp_obj)
                                objectGroup_network_list['obj_name'].append(_tmp_src_grp_obj)
                                objectGroup_network_list['object'].append(_network_obj)

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
                                # Check if current port already member of current object else ADD MEMBER
                                # TUPLE [FIRST NAME] [ GET INDEX OF ELEMNT]. CALL MEMBER FUNC
                                _tmp_src_obj_name = _findObjectName(object_data, src_ip)
                                if not objectGroup_network_list['object'][
                                    objectGroup_network_list['obj_name'].index(_tmp_src_grp_obj)].ismember(
                                    _tmp_src_obj_name):
                                    objectGroup_network_list['object'][
                                        objectGroup_network_list['obj_name'].index(_tmp_src_grp_obj)].addmember(
                                        _tmp_src_obj_name)
                                    #        Check if destination is RFC1918
                            _dst_obj = _findObjectName(object_data, dest_port)
                            zone_rules_writer.append(
                                'access-list ' + re.sub('[ ,]', '_',
                                                        zone_name.capitalize()) + '_in extended permit object-group ' +
                                _service_obj.name + ' object-group ' + _tmp_src_grp_obj + ' object ' +
                                _dst_obj)
                        index += 1
            config = createConfig(zone_rules_writer, object_data, objectGroup_network_list, objectGroup_service_list,
                                  port_data)
            # Remove stale file
            db(db.t_cache.f_name == 'config_' + request.vars.filename + '_' + request.vars.segment_file).delete()
            db.t_cache.insert(f_name='config_' + request.vars.filename + '_' + f_id, f_str_data=config)

        redirect(URL('default', 'acl', vars={'segment_file': f_id, 'filename': request.vars.filename}))
    return locals()


def _findObjectName(object_data, value):
    result = str(object_data.iloc[object_data.loc[object_data['value'] == value].index[0]]['obj_name'])
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
        db.t_data.f_data.retrieve(db(db.t_data.f_name.like(request.vars.filename)).select().first().f_data)[1])
    ports = db(db.t_data.f_name.like(request.vars.filename)).select(db.t_data.f_ports).first()
    src_ip = data[src_col].unique()
    return locals()


### end requires
def index():
    current_files = db(db.t_data.f_name.like('%DBDT%')).select()
    if request.vars.csv_file is not '' and len(request.vars) is not 0:
        f_id = str(datetime.datetime.now().microsecond) + request.vars.csv_file.filename + 'DBDT'
        db.t_data.insert(f_data=request.vars.csv_file, f_name=f_id, f_ports=request.vars.ports)
        db.commit()
        redirect(URL('default', 'table', vars={'filename': f_id, 'ports': request.vars.ports}))
    return locals()


def graph():
    csv_file = db(db.t_data.f_name.like(request.vars.filename)).select().first()
    data = pd.read_csv(
        db.t_data.f_data.retrieve(db(db.t_data.f_name.like(request.vars.filename)).select().first().f_data)[1])
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
