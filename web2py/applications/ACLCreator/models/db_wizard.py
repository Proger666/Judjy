### we prepend t_ to tablenames and f_ to fieldnames for disambiguity


########################################
db.define_table('t_data',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_file', type='string',
                      label=T('File')),
                auth.signature,
                format='%(f_name)s',
                migrate=settings.migrate)

db.define_table('t_data_archive', db.t_data,
                Field('current_record', 'reference t_data', readable=False, writable=False))

########################################
db.define_table('t_cache',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_data', 'upload',
                      label=T('Data')),
                format='%(f_name)s',
                migrate=settings.migrate)
