### we prepend t_ to tablenames and f_ to fieldnames for disambiguity

########################################
db.define_table('t_category',
                Field('f_name', type='string',
                      label=T('name')),
                format='%(f_name)s',
                migrate=settings.migrate)


########################################
db.define_table('t_review',
                Field('f_text', type='string',
                      label=T('Text')),
                Field('f_user', type='string',
                      label=T('User')),
                Field('f_dateadded', type='date',
                      label=T('Dateadded')),
                Field('f_stars', type='string',
                      label=T('Stars')),
                auth.signature,
                format='%(f_text)s',
                migrate=settings.migrate)

db.define_table('t_review_archive', db.t_review,
                Field('current_record', 'reference t_review', readable=False, writable=False))

########################################
db.define_table('t_product',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_dateadded', type='date',
                      label=T('Dateadded')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                Field('f_category', db.t_category),
                format='%(f_name)s',
                migrate=settings.migrate)

db.define_table('t_product_archive', db.t_product,
                Field('current_record', 'reference t_product', readable=False, writable=False))
