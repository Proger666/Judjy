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
set_name = ['Specific ports add to analyze','Maxium \'STATIC\' port','Object preference','Sheets to analyze','separator','First Zone Sep.','Closing Zone Sep.','Zone subnet empty pref','Destination obj prefix','Prefix for Service obj','Source IP column', 'Destination IP column', 'Destination PORT column', 'PROTOCOL column', 'VM name column', 'IP ADDRESS column']
session.set_name = set_name
set_value_def = ['1900,1500,1947,1512,9872,8383,8080,3389,8443,21000,5355,2021,7403,5044,9872,15000,7301,4903,'
                 '7802,10201,22012,8027,2049,10555,10666','1024','auto_', 'Main,ABS+CRM,Processing,CASHIN,'
                                                                                                                                                          'SWIFT+AZIPS,HOKS,Money Transfers,Test Segment', '-', '[', ']',
             '0', 'obj-', 'DM_INLINE_SERVICE_', 'source.ip: Descending', 'dest.ip: Descending', 'dest.port: Descending',
             'transport: Descending', 'VM', 'Ip addres']
if not session.set_value or len(session.set_value) != len(set_name):
    session.set_value = set_value_def
objPref = session.set_value[session.set_name.index('Object preference')]
max_static_port = session.set_value[session.set_name.index('Maxium \'STATIC\' port')]
specific_ports = session.set_value[session.set_name.index('Specific ports add to analyze')]
specific_ports = specific_ports.split(',')
specific_ports = list(set(specific_ports))
specific_ports = map(int, specific_ports)
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
sheet_to_procc = session.set_value[session.set_name.index('Sheets to analyze')]
serviceObjPref = session.set_value[session.set_name.index('Prefix for Service obj')]  # 'SERVICE_srv_'
maxports = sorted(specific_ports, key=int, reverse=True)
maxports = int(maxports[0])  # 'SERVICE_srv_'


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
    if str(ip) == '250.1.1.1' or str(ip) == '251.2.2.2' or str(ip) == '251.2.2.3' or str(ip) == '253.3.3.4' or str(ip) == '253.3.3.5' \
            or str(ip) == '253.3.3.6' or str(ip) == '253.3.3.7' or str(ip) == '253.3.3.8' or str(ip) == '253.3.3.9':
        return True
    try:
        _ip = IP(str(ip))
        _ipa = _ip.iptype()
    except ValueError:
        print ip
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
    response.flash = 'Settings set'



def zones():
    rows = db(db.t_data.f_name.like('%DBSG%')).select()
    default_set_value = set_value_def
    set_value = session.set_value
    set_name = session.set_name
    if request.vars.segment_file is not None and len(request.vars) is not 0:
        sameIPhost = request.vars.maxH
        # extract max ports that was saved in DB with data file
        maxPorts = maxports
        if hasattr(request.vars.segment_file, 'file'):
            f_id = str(datetime.datetime.now().microsecond) + request.vars.segment_file.filename + 'DBSG'
            db.t_data.insert(f_data=request.vars.segment_file, f_name=f_id, f_ports=request.vars.ports)
            db.commit()
        else:
            f_id = request.vars.segment_file
        xl  = pd.ExcelFile(db.t_data.f_data.retrieve(db(db.t_data.f_name.like(f_id)).select().first().f_data)[1])

        # remove unicode and cast to STR
        #sheet_names = [str(x) for x in xl.sheet_names]
        sheets = xl.book.sheets()
        initial_data = pd.read_csv(
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
        xl_nets = xl.parse('Nets')

        xl_dataframe = pd.DataFrame(columns=[seg_VM_col, seg_IP_col, 'Zone_name'])
        for sheet in sheets:
           try:
            sheet.name.decode('ascii')
           except (UnicodeDecodeError, UnicodeEncodeError):
               None # do nothing cuz incorrect sheet
           else:
            try:
                df_tmp = xl.parse(sheet.name)
                df_tmp = df_tmp[[seg_VM_col, seg_IP_col]]
                df_tmp['Zone_name'] = sheet.name
                _grouped = df_tmp[seg_IP_col]
                for dst in _grouped.iteritems():
                    _tmp = xl_dataframe.loc[xl_dataframe[seg_IP_col] == dst[1]]
                    if not _tmp.empty:
                        df_tmp.set_value(df_tmp[seg_IP_col] == dst[1], 'Zone_name', 'UNKNOWN')
                xl_dataframe = xl_dataframe.append(df_tmp)
            except KeyError:
                None # do nothing cuz incorrect sheet
            del df_tmp



        # Test DATA
        #df_tmp[src_col,'Zone_name'] = ['1.1.1.1','2.2.2.2', 'udp', 999,'TEST2']

        #df_tmp['Zone_name'] = ['2.2.2.2','1.1.1.1', 'udp', 666,'TEST1']
        # ADD TEST DATA TO main DATA


        # Check if file already processed
        _tmp_row = db.t_cache(f_name='processed_' + request.vars.filename+f_id)
        if not _tmp_row:
            # REMOVE BIG PORST from data
            data = initial_data[initial_data[dstport_col] < maxPorts]
            # Tag everything with src zone and dst zone
            for index, row in data.iterrows():
                try:
                    # find Zone name  for SRC based on IP
                    src_z_name = str(
                        xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[src_col]].values[0][2])
                except IndexError:
                    data.set_value(index, 'src_zone_name',
                                   'UNKNOWN')
                else:
                    data.set_value(index, 'src_zone_name',
                                   src_z_name)
                try:
                    # find Zone name  for DST based on IP
                    dst_z_name = str(
                        xl_dataframe.loc[xl_dataframe[seg_IP_col] == row[dst_col]].values[0][2])
                except IndexError:
                    data.set_value(index, 'dst_zone_name',
                                   'UNKNOWN')
                else:
                    data.set_value(index, 'dst_zone_name',
                                   dst_z_name)

            # Add processed file to cache
            db.t_cache.insert(f_name='processed_' + request.vars.filename+f_id, f_str_data=data.to_csv(index=False))
            db.commit()
        else:
            # Create buffer to feed it to pandas
            _tmp_buffer = StringIO.StringIO()
            _tmp_buffer.write(db(db.t_cache.f_name == _tmp_row.f_name).select(db.t_cache.f_str_data).first().f_str_data)
            _tmp_buffer.seek(0)
            # load file from cache
            data = pd.read_csv(_tmp_buffer)
            del _tmp_buffer
        # delete object from memory if record already present
        del _tmp_row



        ############################ TEST SECTION ################################
        # Add Test DATA to SEGMENT FILE
        df_tmp = pd.DataFrame(index=[seg_IP_col,seg_VM_col,'Zone_name'])
        _tmp_data = pd.DataFrame(
            {seg_IP_col: ['250.1.1.1'], seg_VM_col: ['_delME_TEST1-OBJECT'], 'Zone_name': ['TEST1']})
        xl_dataframe = xl_dataframe.append(_tmp_data)
        _tmp_data = pd.DataFrame(
            {seg_IP_col: ['251.2.2.2'], seg_VM_col: ['_delME_TEST2-OBJECT'], 'Zone_name': ['TEST2']})
        xl_dataframe = xl_dataframe.append(_tmp_data)
        _tmp_data = pd.DataFrame(
            {seg_IP_col: ['251.2.2.3'], seg_VM_col: ['_delME_TEST3-OBJECT'], 'Zone_name': ['TEST2']})
        xl_dataframe = xl_dataframe.append(_tmp_data)
        _tmp_data = pd.DataFrame(
            {seg_IP_col: ['253.3.3.4'], seg_VM_col: ['_delME_TEST4-OBJECT'], 'Zone_name': ['TEST3']})
        xl_dataframe = xl_dataframe.append(_tmp_data)
        _tmp_data = pd.DataFrame(
            {seg_IP_col: ['253.3.3.5','253.3.3.6','253.3.3.7','253.3.3.8','253.3.3.9'],
             seg_VM_col: ['_delME_TEST5-OBJECT','_delME_TEST6-OBJECT','_delME_TEST7-OBJECT','_delME_TEST8-OBJECT','_delME_TEST9-OBJECT']})
        _tmp_data['Zone_name'] = 'TEST3'
        xl_dataframe = xl_dataframe.append(_tmp_data)
        del _tmp_data

        # Add Test DATA to DATA FILE
        # TEST TEST1 MANY PORTS TO TEST2
        _tmp_data = pd.DataFrame({transport_col: ['udp','udp','tcp'], dstport_col: [999,666,999]})
        _tmp_data[src_col] = '250.1.1.1' # auto_[TEST1]__delME_TEST1-OBJECT
        _tmp_data[dst_col] = '251.2.2.2' # auto_[TEST2]__delME_TEST2-OBJECT
        _tmp_data['src_zone_name'] = 'TEST1'
        _tmp_data['dst_zone_name'] = 'TEST2'
        data = data.append(_tmp_data)
        # test whole ZONE to HOST
        _tmp_data = pd.DataFrame({src_col: ['253.3.3.4','253.3.3.5','253.3.3.6','253.3.3.7','253.3.3.8','253.3.3.9'],
                                  transport_col: ['udp', 'udp', 'tcp','tcp','udp','udp'],
                                  dstport_col: [999, 666, 998,669,666,999]})
        _tmp_data[dst_col] = '250.1.1.1'
        _tmp_data['src_zone_name'] = 'TEST3'
        _tmp_data['dst_zone_name'] = 'TEST1'
        data = data.append(_tmp_data)

        _tmp_data = pd.DataFrame(
            {src_col: ['251.2.2.2','250.1.1.1','250.1.1.1','251.2.2.3','172.16.15.1'],
             dst_col: ['250.1.1.1','250.1.1.1','251.2.2.3','172.16.15.1', '250.1.1.1'],
             transport_col: ['udp','tcp','udp','udp','udp'],
             dstport_col: [666,999,666,999,666],
             'src_zone_name': ['TEST2','TEST1','TEST1','TEST2','UNKNOWN'],
             'dst_zone_name': ['TEST1','TEST1','TEST2','UNKNOWN','TEST1']})
        data = data.append(_tmp_data)
        _tmp_data = pd.DataFrame(
            {src_col: ['172.16.15.1','172.16.15.2','172.16.15.1'],
             dst_col: ['251.2.2.2','251.2.2.2','251.2.2.2'],
             transport_col: ['udp','tcp','tcp'], dstport_col: [999,999,777]})
        _tmp_data[ 'src_zone_name'] ='UNKNOWN'
        _tmp_data['dst_zone_name'] = 'TEST2'
        data = data.append(_tmp_data)
        del _tmp_data
        ############################ END TEST SECTION ################################

        _tmp_row = db.t_cache(f_name='config' + request.vars.filename + '_' + f_id)
        if not _tmp_row:

            # remove BIGPorts as stated in Session.Settings
            data = data.loc[( data[dstport_col].isin(specific_ports)) | (data[dstport_col] <= int(max_static_port))]
            ##########################BEGIN ZONE PROCESSING #######################
            index_service = 1
            index_srv_dst = 1
            for zone_name in xl_dataframe['Zone_name'].unique():
               if zone_name in sheet_to_procc or zone_name == 'TEST1' or zone_name == 'TEST2' or zone_name == 'TEST3':
                # Create objects for all VMs from segment_file
                for index, row in xl_dataframe.loc[xl_dataframe['Zone_name'] == zone_name].iterrows():
                    if row[seg_IP_col] not in objectNetwork_tuple['value']:
                        if validate_ip(row[seg_IP_col]):
                            objectNetwork_tuple['value'].append(row[seg_IP_col])
                        else:
                            objectNetwork_tuple['value'].append('NOT ASSIGNED')
                        zone_name = re.sub('[ ,]', '_', row['Zone_name'])
                        objectNetwork_tuple['obj_name'].append(
                            objPref + zone_sep_f + zone_name + zone_sep_s + '_' + re.sub('[ ,]', '_',
                                                                                         row[seg_VM_col]))
                        objectNetwork_tuple['description'].append(
                            re.sub('[ ,]', '_', row[seg_VM_col]) + ' from ' + row['Zone_name'])
                        objectNetwork_tuple['type'].append('host')
                # create group object for zone_ip
                # clear zone name from garbage
                zone_name = re.sub('[ ,]', '_', zone_name)
                try:
                    zone_NET = str(IP(xl_nets.loc[xl_nets['Net_name'] == zone_name]['Net_new'][0]).net()) + ' ' + str(IP(xl_nets.loc[xl_nets['Net_name'] == 'ATM']['Net_new'][0]).netmask())
                except IndexError:
                    zone_NET = zone_name + '_IP'
                # remove unicode and cast to STR
                zone_name = str(zone_name)
                # Create objects for all uniq ports/transport
                # Get all uniq pors via drop_duplicates and filter by maxPorts setting
                uniq_ports_src = data.loc[data['src_zone_name'] == zone_name, [transport_col, dstport_col]].drop_duplicates()
                for index, row in uniq_ports_src.iterrows():
                    objectPort_tuple['obj_name'].append(row[transport_col] + '_' + str(row[dstport_col]))
                    objectPort_tuple['value'].append(
                        'service ' + row[transport_col] + ' destination eq ' + str(row[dstport_col]))
                objectNetwork_tuple['obj_name'].append('zone_' + zone_sep_f + zone_name + zone_sep_s + '_NET')
                objectNetwork_tuple['type'].append('subnet')
                objectNetwork_tuple['description'].append('Zone ' + zone_name + ' subnet')
                objectNetwork_tuple['value'].append(zone_NET)



                ######################### SORTING DATA FOR CURRENT ZONE ################################
                zone_ips = xl_dataframe.loc[xl_dataframe['Zone_name'] == zone_name, seg_IP_col].tolist()


                # filter by label source.ip and find all ip that is belongs to zone inside source DATA and dst not the same zone
                source_tree = data[
                    (data[src_col].isin(zone_ips)  & (
                        data['dst_zone_name'] != zone_name))]

                # DEST tree - all interactions TO this zone
                dest_tree = data[(data['dst_zone_name'] == zone_name) & (data['src_zone_name'] == 'UNKNOWN')]

                # Group by DEST IP - tree to DEST ip address so dest ip - list of all who interacte with it
                #dest_tree = source_tree.groupby(
                 #   [dst_col, dstport_col, src_col, transport_col, 'src_zone_name', 'dst_zone_name'], as_index=False).mean()
                # group by dest ip and count non unique values (source ip) to count how much src ip connects to same dst and port
                aggregate_src_hit = source_tree.groupby([dst_col])[src_col].nunique()
                # Hit to SRC inside zone
                aggregate_dst_zone_hit = dest_tree.groupby([dst_col, dstport_col, transport_col, 'src_zone_name'])[src_col].nunique()
                # services  TO this zone
                service_dst_grp = dest_tree.groupby([dst_col, dstport_col, transport_col])[dstport_col].nunique()
                # Add missing ports
                for dest_port_proto, row in service_dst_grp.iteritems():
                    if dest_port_proto[2] + '_' + str(dest_port_proto[1]) not in objectPort_tuple['obj_name']:
                        objectPort_tuple['obj_name'].append(dest_port_proto[2] + '_' + str(dest_port_proto[1]))
                        objectPort_tuple['value'].append(
                        'service ' + dest_port_proto[2] + ' destination eq ' + str(dest_port_proto[1]))


                # SERVICES FOR THIS ZONE
                service_src_grp = source_tree.groupby([dst_col, dstport_col, transport_col])[dstport_col].unique()
                port_data = pd.DataFrame(objectPort_tuple)
                ######################### END OF SORTING ################################

                ########## SOURCE OBJECTS #############
                # Create SERVICE objects for SRC
                last_dst = ''
                for dst_port, garbage in service_src_grp.iteritems():
                    if RFC1918(dst_port[0]) and not broadcast(dst_port[0]):
                        if last_dst is '' or dst_port[0] != last_dst:
                            # Create dst SERVICE group
                            _tmp_port_grp_obj = serviceObjPref + str(index_service)
                            # Create SERVICE object for DST if not exist
                            if _tmp_port_grp_obj not in objectGroup_service_list['obj_name']:
                                _service_obj = GroupObject(_tmp_port_grp_obj)
                                objectGroup_service_list['obj_name'].append(_tmp_port_grp_obj)
                                objectGroup_service_list['dst'].append(dst_port[0]+zone_name)
                                objectGroup_service_list['object'].append(_service_obj)
                                last_dst = dst_port[0]
                                index_service += 1
                        else:
                            _tmp_port_grp_obj = serviceObjPref + str(index_service - 1)

                        addMembersToServiceOBJ(_tmp_port_grp_obj, dst_port[2] ,dst_port[1], objectGroup_service_list)# Create DST obj for every dst in zone
                        if dst_port[0] not in objectNetwork_tuple['value']:
                            if validate_ip(dst_port[0]):
                                objectNetwork_tuple['value'].append(dst_port[0])
                            else:
                                objectNetwork_tuple['value'].append('NOT ASSIGNED')

                            _obj_name = data.loc[data[dst_col] == dst_port[0], ['dst_zone_name']].drop_duplicates()
                            _dst_zone_name = _obj_name.iloc[0]['dst_zone_name']
                            if _dst_zone_name != 'UNKNOWN':
                                objectNetwork_tuple['obj_name'].append(
                                    objPref + zone_sep_f + _dst_zone_name + zone_sep_s + '_' + xl_dataframe.loc[xl_dataframe[seg_IP_col] == dst_port[0]].values[0][1])
                                objectNetwork_tuple['description'].append(
                                    xl_dataframe.loc[xl_dataframe[seg_IP_col] == dst_port[0]].values[0][1] + ' from ' + _dst_zone_name)
                            else:
                                objectNetwork_tuple['obj_name'].append(
                                    objPref + dst_obj_pref + dst_port[0])
                                objectNetwork_tuple['description'].append("LAN host")
                            objectNetwork_tuple['type'].append('host')


                # Make objects dataframe
                object_data = pd.DataFrame(objectNetwork_tuple)
                ###################### SOURCE RULES ########################
                # Start index for DM_INLINE
                index_srv = 1
                for dest_port, hitcount in aggregate_src_hit.iteritems():

                    # Check if destination is RFC1918 and not broadcast or net adress
                    if RFC1918(dest_port) and not broadcast(dest_port):
                        _service_obj = objectGroup_service_list['object'][
                            objectGroup_service_list['dst'].index(dest_port+zone_name)]
                        if hitcount >= int(sameIPhost):
                            _dst_obj = _findObjectName(object_data, dest_port)
                            zone_rules_writer.append(
                                'access-list ' + re.sub(' ', '_',
                                                        zone_name.capitalize()) + '_in extended permit object-group '
                                + _service_obj.name + ' object-group ' + _findObjectName(object_data,
                                                                                         zone_NET) + ' object-group ' + _dst_obj)
                        else:
                            grouped = source_tree.loc[source_tree[dst_col] == dest_port, [src_col]]

                            # Create SRC SRV_<srv_name> object for SRC if not exist
                            _tmp_src_grp_obj = objPref + zone_sep_f + zone_name + zone_sep_s + '_' + 'srv_' + str(index_srv)
                            if _tmp_src_grp_obj not in objectGroup_network_list['obj_name']:
                                _network_obj = GroupObject(_tmp_src_grp_obj)
                                objectGroup_network_list['obj_name'].append(_tmp_src_grp_obj)
                                objectGroup_network_list['object'].append(_network_obj)

                            for src_ip in grouped[src_col]:

                                # Add src obj to group
                                # Check if current port already member of current object else ADD MEMBER
                                # TUPLE [FIRST NAME] [ GET INDEX OF ELEMNT]. CALL MEMBER FUNC
                               #try:
                                _tmp_src_obj_name = _findObjectName(object_data, src_ip)
                               #except IndexError:
                                   #print src_ip
                               #else:
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
                        index_srv += 1
                zone_rules_writer.append(
                        'access-list ' + zone_name.capitalize() + '_in extended permit ip any any log 6 interval 300')
                ######################## DESTINATION RULES ##################
                ### sorting for destination rules
                _dst_rul = dest_tree.groupby(by=[src_col, dst_col, transport_col])[dstport_col].apply(
                    lambda x: ','.join(sorted(x.astype(str).tolist()))).to_frame().reset_index()
                if not _dst_rul.empty:
                    _dst_rul = _dst_rul.groupby(by=[dst_col, dstport_col, transport_col])[src_col].apply(
                           lambda x: ','.join(x.tolist())).to_frame().reset_index()
                    #####
                    # Concant TCP and UDP rules for same SRCs
                    _dst_rules_df = pd.DataFrame(columns=[src_col,dst_col,dstport_col,transport_col])
                    for src_ip in _dst_rul[src_col].unique():
                        _tmp_data = _dst_rul.loc[(_dst_rul[src_col] == src_ip)]
                        _tmp_list = [x[1] for x in _tmp_data.groupby(dst_col)]
                        for DF  in _tmp_list:
                            for index, row in DF.iterrows():
                                _result = []
                                _result.append(row[src_col]+',')

                    # Create DST rul
                    for index, row_dst in _dst_rul.iterrows():
                     # Check if destination is RFC1918 and not broadcast or net adress
                     if RFC1918(row_dst[dst_col]) and not broadcast(row_dst[dst_col]):
                       uniq_src_dst = row_dst[src_col].split(',')
                       if len(uniq_src_dst) <= int(sameIPhost):
                           # Create objects for all src to this DST
                           for src_ip in uniq_src_dst:
                               # ADD any missing src to objects
                               if src_ip not in objectNetwork_tuple['value']:
                                   if validate_ip(src_ip):
                                       objectNetwork_tuple['value'].append(src_ip)
                                       objectNetwork_tuple['obj_name'].append(
                                           objPref + zone_sep_f + 'LAN' + zone_sep_s + '_' + src_ip)
                                       objectNetwork_tuple['description'].append(src_ip + ' from ' + 'LAN')
                                       objectNetwork_tuple['type'].append('host')
                           object_data = pd.DataFrame(objectNetwork_tuple)
                           # Create service Object for DST and append ports to it
                           _tmp_service_grp_obj_name = serviceObjPref + str(index_service)
                           objectGroup_service_list['obj_name'].append(_tmp_service_grp_obj_name)
                           objectGroup_service_list['dst'].append(row_dst[dst_col] + zone_name)
                           objectGroup_service_list['object'].append(GroupObject(_tmp_service_grp_obj_name))
                           index_service += 1
                           # get all uniq ports for this DST
                           uniq_ports_dst = row_dst[dstport_col].split(',')
                           # Append all uniq ports to service object
                           for port in uniq_ports_dst:
                               addMembersToServiceOBJ(_tmp_service_grp_obj_name, row_dst[transport_col], port,
                                                      objectGroup_service_list)
                           # Create DST SRV_<srv_name> object for SRC if not exist
                           _tmp_src_grp_obj = objPref + zone_sep_f + 'LAN' + zone_sep_s + '_' + 'srv_' + str(index_srv_dst)
                           index_srv_dst += 1
                           if _tmp_src_grp_obj not in objectGroup_network_list['obj_name']:
                               _network_obj = GroupObject(_tmp_src_grp_obj)
                               objectGroup_network_list['obj_name'].append(_tmp_src_grp_obj)
                               objectGroup_network_list['object'].append(_network_obj)
                           # Create list from SRC COL
                           _src_dst_list = row_dst[src_col].split(',')
                           for src_ip in _src_dst_list:
                               _tmp_src_obj_name = _findObjectName(object_data, src_ip)
                               # Add src obj to group
                               # Check if current port already member of current object else ADD MEMBER
                               # TUPLE [FIRST NAME] [ GET INDEX OF ELEMNT]. CALL MEMBER FUNC
                               if not objectGroup_network_list['object'][
                                   objectGroup_network_list['obj_name'].index(_tmp_src_grp_obj)].ismember(
                                   _tmp_src_obj_name):
                                   objectGroup_network_list['object'][
                                       objectGroup_network_list['obj_name'].index(_tmp_src_grp_obj)].addmember(
                                       _tmp_src_obj_name)
                           _dst_obj = _findObjectName(object_data, row_dst[dst_col])
                           zone_rules_writer.append(
                               'access-list ' + 'LAN' + '_in extended permit object-group ' +
                               _tmp_service_grp_obj_name + ' object-group ' + _tmp_src_grp_obj + ' object ' +
                               _dst_obj)

            config = createConfig(zone_rules_writer, object_data, objectGroup_network_list,
                                      objectGroup_service_list,
                                      port_data)

            # Remove stale file
            db(db.t_cache.f_name == 'config_' + request.vars.filename + '_' + request.vars.segment_file).delete()
            db.t_cache.insert(f_name='config_' + request.vars.filename + '_' + f_id, f_str_data=config)

        redirect(URL('default', 'acl', vars={'segment_file': f_id, 'filename': request.vars.filename}))
    return locals()


def addMembersToServiceOBJ(serviceObjectName, protocol, port, objectGroup_service_list):
    # Check if current port already member of current object else ADD MEMBER
    # TUPLE [FIRST NAME] [ GET INDEX OF ELEMNT]. CALL MEMBER FUNC
    if not objectGroup_service_list['object'][
        objectGroup_service_list['obj_name'].index(serviceObjectName)].ismember(
                        protocol + '_' + str(port)):
        objectGroup_service_list['object'][
            objectGroup_service_list['obj_name'].index(serviceObjectName)].addmember(
            protocol + '_' + str(port))


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
    data = data.loc[(data[src_col] == request.vars.ip)
                    & (data[dstport_col] <= int(request.vars.ports)),
                    [dst_col, dstport_col]]
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
