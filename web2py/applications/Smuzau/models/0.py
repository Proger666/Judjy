from gluon.storage import Storage
settings = Storage()
settings.migrate = True
settings.title = 'Smuzau'
settings.subtitle = 'powered by web2py'
settings.author = 'Scorpa'
settings.author_email = 'info@postix3.ru'
settings.keywords = '\xd0\xa1\xd0\xbc\xd1\x83\xd0\xb7\xd1\x8f\xd1\x83, \xd1\x81\xd0\xbc\xd1\x83\xd0\xb7\xd0\xb8, \xd0\xb5\xd0\xb1\xd0\xbe\xd1\x82\xd0\xb0, smoothie'
settings.description = '\xd0\xa1\xd0\xbc\xd1\x83\xd0\xb7\xd0\xb8! \xd0\xbf\xd1\x80\xd0\xbe\xd1\x81\xd1\x82\xd0\xbe \xd0\xbd\xd0\xb0\xd0\xbc\xd1\x83\xd1\x82\xd0\xb8 \xd1\x81\xd0\xb5\xd0\xb1\xd0\xb5! \r\n\xd0\xa1\xd0\xbc\xd1\x83\xd0\xb7\xd0\xb8\xd0\xba \xd0\xb2 \xd0\xbf\xd1\x83\xd0\xb7\xd0\xb8\xd0\xba, \xd0\xb3\xd1\x80\xd0\xb5\xd0\xb1\xd0\xb0\xd0\xbd\xd0\xbd\xd1\x8b\xd0\xb9 \xd1\x82\xd1\x8b \xd1\x82\xd0\xb5\xd0\xbb\xd0\xb5\xd0\xbf\xd1\x83\xd0\xb7\xd0\xb8\xd0\xba'
settings.layout_theme = 'Default'
settings.database_uri = 'mysql://root:ghfuf@127.0.0.1:3306/smuzau'
settings.security_key = 'd0959fc4-7fd5-49a0-9f20-29882e87d59d'
settings.email_server = 'localhost'
settings.email_sender = 'you@example.com'
settings.email_login = ''
settings.login_method = 'local'
settings.login_config = ''
settings.plugins = []
settings.max_rating = 5
response.logo = A(IMG(_src=URL('static','images/logo.png'),
                           _alt=T('In-Smuzau-We-trust')), _href=URL('default', 'index'), _class="navbar-brand", _style="padding:5px")
