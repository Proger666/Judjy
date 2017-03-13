### we prepend t_ to tablenames and f_ to fieldnames for disambiguity
########################################
db.define_table('tag_ingr',
                Field('name'),
                format='%(name)s')
########################################
db.define_table('tag_smuz',
                Field('name'),
                format='%(name)s')
########################################
db.define_table('t_review',
                Field('f_fulltext', type='string',
                      label=T('Fulltext')),
                auth.signature,
                format='%(f_fulltext)s',
                migrate=settings.migrate)

db.define_table('t_review_archive', db.t_review,
                Field('current_record', 'reference t_review', readable=False, writable=False))
########################################
db.define_table('t_category',
                Field('f_name', type='string',
                      label=T('name')),
                format='%(f_name)s',
                migrate=settings.migrate)
########################################

db.define_table('t_taste',
                Field('f_name', type='string',
                      label=T('name')),
                format='%(f_name)s',
                migrate=settings.migrate)
########################################
db.define_table('t_smoothie',
                Field('f_name', type='string',
                    label=T('Name')),
                Field('f_name_lat', type='string',
                      label=T('Name_Lat_int')),
                Field('f_taste', db.t_taste,
                      label=T('Taste')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                Field('f_rating', type='integer',
                      label=T('rating')),
                Field('tags', 'list:reference tag_smuz'),
                Field('ingredients', 'list:reference tag_ingr'),
                format='%(f_name)s',
                migrate=settings.migrate)

########################################
db.define_table('t_smoothie_review',
                Field('f_smoothie', db.t_smoothie),
                Field('f_review', db.t_review))
########################################
db.define_table('t_smoothie_category',
                Field('f_smoothie', db.t_smoothie),
                Field('f_cat', db.t_category))

########################################

db.define_table('t_ingredient',
                Field('f_name', type='string',
                    label=T('Name')),
                Field('f_taste', db.t_taste,
                      label=T('Taste')),
                Field('f_image', 'upload'),
                Field('f_img', type='blob',
                      label=T('img')),
                format='%(f_name)s',
                migrate=settings.migrate)

########################################
db.define_table('t_ingr_category',
                Field('f_ingr', db.t_ingredient),
                Field('f_cat', db.t_category))

########################################
db.define_table('t_recipe',
                Field('f_name', type='string',
                      label=T('Name')),
                Field('f_date', type='string',
                      label=T('Date')),
                Field('f_fulltext', type='string',
                      label=T('Fulltext')),
                Field('f_smoothie', db.t_smoothie,
                      label=T('Smoothie')),
                auth.signature,
                format='%(f_name)s',
                migrate=settings.migrate)

db.define_table('t_recipe_archive', db.t_recipe,
                Field('current_record', 'reference t_recipe', readable=False, writable=False))
